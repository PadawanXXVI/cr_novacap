# dashboard_bi/filtros.py

from datetime import date
import pandas as pd
import streamlit as st


def obter_opcoes(df, coluna):
    if coluna not in df.columns:
        return []

    opcoes = (
        df[coluna]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    return sorted(
        op for op in opcoes
        if op not in ["", "nan", "None", "NaT"]
    )


def formatar_data_br(data):
    return data.strftime("%d/%m/%Y")


def definir_periodo_padrao(df):
    data_padrao_inicio = date(2026, 1, 1)
    data_padrao_fim = date(2026, 6, 30)

    if df.empty or "data_entrada_novacap" not in df.columns:
        return data_padrao_inicio, data_padrao_fim

    menor_data = df["data_entrada_novacap"].min()
    maior_data = df["data_entrada_novacap"].max()

    if pd.isna(menor_data) or pd.isna(maior_data):
        return data_padrao_inicio, data_padrao_fim

    menor_data = menor_data.date()
    maior_data = maior_data.date()

    data_inicio = max(data_padrao_inicio, menor_data)
    data_fim = min(data_padrao_fim, maior_data)

    if data_inicio > data_fim:
        return menor_data, maior_data

    return data_inicio, data_fim


def gerar_rotulo_periodo(data_inicio, data_fim):
    if data_inicio == date(2026, 1, 1) and data_fim == date(2026, 6, 30):
        return "1º Semestre de 2026"

    if data_inicio.year == data_fim.year and data_inicio.month == data_fim.month:
        meses = {
            1: "Janeiro",
            2: "Fevereiro",
            3: "Março",
            4: "Abril",
            5: "Maio",
            6: "Junho",
            7: "Julho",
            8: "Agosto",
            9: "Setembro",
            10: "Outubro",
            11: "Novembro",
            12: "Dezembro",
        }
        return f"{meses[data_inicio.month]} de {data_inicio.year}"

    return "Período personalizado"


def aplicar_filtros_sidebar(df):
    st.sidebar.title("🔎 Filtros da análise")
    st.sidebar.caption("Os filtros são aplicados em cascata.")

    if st.sidebar.button("🧹 Limpar filtros", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.sidebar.divider()

    dados_filtrados = df.copy()

    data_inicio_padrao, data_fim_padrao = definir_periodo_padrao(df)

    st.sidebar.markdown("### Período de entrada")

    data_inicio = st.sidebar.date_input(
        "Data inicial",
        value=data_inicio_padrao,
        format="DD/MM/YYYY",
        key="filtro_data_inicio",
    )

    data_fim = st.sidebar.date_input(
        "Data final",
        value=data_fim_padrao,
        format="DD/MM/YYYY",
        key="filtro_data_fim",
    )

    if data_inicio > data_fim:
        st.sidebar.error("A data inicial não pode ser maior que a data final.")
        st.stop()

    dados_filtrados = dados_filtrados[
        (dados_filtrados["data_entrada_novacap"].dt.date >= data_inicio)
        & (dados_filtrados["data_entrada_novacap"].dt.date <= data_fim)
    ]

    rotulo_periodo = gerar_rotulo_periodo(data_inicio, data_fim)

    st.sidebar.caption(
        f"Período selecionado: {formatar_data_br(data_inicio)} a {formatar_data_br(data_fim)}"
    )

    st.sidebar.divider()

    ras = st.sidebar.multiselect(
        "Região Administrativa",
        options=obter_opcoes(dados_filtrados, "ra_origem"),
        placeholder="Todas as RAs",
        key="filtro_ras",
    )

    if ras:
        dados_filtrados = dados_filtrados[dados_filtrados["ra_origem"].isin(ras)]

    diretorias = st.sidebar.multiselect(
        "Diretoria",
        options=obter_opcoes(dados_filtrados, "diretoria"),
        placeholder="Todas as diretorias",
        key="filtro_diretorias",
    )

    if diretorias:
        dados_filtrados = dados_filtrados[dados_filtrados["diretoria"].isin(diretorias)]

    grupos_demanda = st.sidebar.multiselect(
        "Grupo da demanda",
        options=obter_opcoes(dados_filtrados, "grupo_demanda"),
        placeholder="Todos os grupos",
        key="filtro_grupos_demanda",
    )

    if grupos_demanda:
        dados_filtrados = dados_filtrados[
            dados_filtrados["grupo_demanda"].isin(grupos_demanda)
        ]

    demandas = st.sidebar.multiselect(
        "Demanda detalhada",
        options=obter_opcoes(dados_filtrados, "demanda"),
        placeholder="Todas as demandas",
        key="filtro_demandas",
    )

    if demandas:
        dados_filtrados = dados_filtrados[dados_filtrados["demanda"].isin(demandas)]

    status = st.sidebar.multiselect(
        "Status atual",
        options=obter_opcoes(dados_filtrados, "status_atual"),
        placeholder="Todos os status",
        key="filtro_status",
    )

    if status:
        dados_filtrados = dados_filtrados[dados_filtrados["status_atual"].isin(status)]

    filtros = {
        "rotulo_periodo": rotulo_periodo,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "periodo_formatado": (
            f"{formatar_data_br(data_inicio)} a {formatar_data_br(data_fim)}"
        ),
        "ras": ras,
        "diretorias": diretorias,
        "grupos_demanda": grupos_demanda,
        "demandas": demandas,
        "status": status,
    }

    return dados_filtrados, filtros
