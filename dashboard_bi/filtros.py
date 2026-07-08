# dashboard_bi/filtros.py

import streamlit as st


def obter_opcoes(df, coluna):
    if coluna not in df.columns:
        return []

    return sorted(
        df[coluna]
        .dropna()
        .astype(str)
        .unique()
    )


def aplicar_filtros_sidebar(df):
    st.sidebar.title("🔎 Filtros da análise")

    st.sidebar.caption("Os filtros são aplicados em cascata.")

    dados_filtrados = df.copy()

    # ======================================================
    # 1. Região Administrativa
    # ======================================================
    ras_opcoes = obter_opcoes(dados_filtrados, "ra_origem")

    ras = st.sidebar.multiselect(
        "Região Administrativa",
        options=ras_opcoes,
        placeholder="Todas as RAs"
    )

    if ras:
        dados_filtrados = dados_filtrados[
            dados_filtrados["ra_origem"].isin(ras)
        ]

    # ======================================================
    # 2. Diretoria
    # ======================================================
    diretorias_opcoes = obter_opcoes(dados_filtrados, "diretoria")

    diretorias = st.sidebar.multiselect(
        "Diretoria",
        options=diretorias_opcoes,
        placeholder="Todas as diretorias"
    )

    if diretorias:
        dados_filtrados = dados_filtrados[
            dados_filtrados["diretoria"].isin(diretorias)
        ]

    # ======================================================
    # 3. Departamento
    # ======================================================
    departamentos_opcoes = obter_opcoes(dados_filtrados, "departamento")

    departamentos = st.sidebar.multiselect(
        "Departamento",
        options=departamentos_opcoes,
        placeholder="Todos os departamentos"
    )

    if departamentos:
        dados_filtrados = dados_filtrados[
            dados_filtrados["departamento"].isin(departamentos)
        ]

    # ======================================================
    # 4. Grupo da Demanda
    # ======================================================
    grupos_opcoes = obter_opcoes(dados_filtrados, "grupo_demanda")

    grupos_demanda = st.sidebar.multiselect(
        "Grupo da demanda",
        options=grupos_opcoes,
        placeholder="Todos os grupos"
    )

    if grupos_demanda:
        dados_filtrados = dados_filtrados[
            dados_filtrados["grupo_demanda"].isin(grupos_demanda)
        ]

    # ======================================================
    # 5. Demanda Detalhada
    #    Depende do grupo da demanda selecionado.
    # ======================================================
    demandas_opcoes = obter_opcoes(dados_filtrados, "demanda")

    demandas = st.sidebar.multiselect(
        "Demanda detalhada",
        options=demandas_opcoes,
        placeholder="Todas as demandas"
    )

    if demandas:
        dados_filtrados = dados_filtrados[
            dados_filtrados["demanda"].isin(demandas)
        ]

    # ======================================================
    # 6. Status atual
    # ======================================================
    status_opcoes = obter_opcoes(dados_filtrados, "status_atual")

    status = st.sidebar.multiselect(
        "Status atual",
        options=status_opcoes,
        placeholder="Todos os status"
    )

    if status:
        dados_filtrados = dados_filtrados[
            dados_filtrados["status_atual"].isin(status)
        ]

    filtros = {
        "ras": ras,
        "diretorias": diretorias,
        "departamentos": departamentos,
        "grupos_demanda": grupos_demanda,
        "demandas": demandas,
        "status": status,
    }

    return dados_filtrados, filtros
