# dashboard_bi/dashboard.py

import streamlit as st

from consultas import carregar_dados
from filtros import aplicar_filtros_sidebar
from indicadores import exibir_kpis, adicionar_categoria_status
from graficos import (
    grafico_evolucao_mensal,
    grafico_rosca_status,
    grafico_status_detalhado,
    grafico_processos_por_diretoria,
    grafico_processos_por_departamento,
    grafico_top_ras,
    grafico_grupos_demanda,
    grafico_demandas_detalhadas,
    grafico_treemap_hierarquia,
    grafico_tempo_medio_por_diretoria,
)


st.set_page_config(
    page_title="Dashboard CR/NOVACAP",
    layout="wide"
)


df = carregar_dados()

dados, filtros = aplicar_filtros_sidebar(df)
dados = adicionar_categoria_status(dados)


st.title("Companhia Urbanizadora da Nova Capital - NOVACAP")
st.subheader("Central de Relacionamento - CR")
st.caption("Análise Gerencial — 1º Semestre de 2026")
st.caption("Período analisado: 01/01/2026 a 30/06/2026")


st.subheader("Indicadores gerais")
exibir_kpis(dados)


st.divider()


st.subheader("Distribuição territorial")

col_mapa, col_ra = st.columns([1, 1])

with col_mapa:
    st.info("Mapa das Regiões Administrativas do DF será implementado na próxima etapa.")

with col_ra:
    st.plotly_chart(
        grafico_top_ras(dados, top_n=15),
        use_container_width=True
    )


st.divider()


st.subheader("Tendência temporal")

st.plotly_chart(
    grafico_evolucao_mensal(dados),
    use_container_width=True
)


st.divider()


st.subheader("Status gerencial")

col_status_1, col_status_2 = st.columns(2)

with col_status_1:
    st.plotly_chart(
        grafico_rosca_status(dados),
        use_container_width=True
    )

with col_status_2:
    st.plotly_chart(
        grafico_status_detalhado(dados),
        use_container_width=True
    )


st.divider()


st.subheader("Estrutura institucional")

col_dir, col_dep = st.columns(2)

with col_dir:
    st.plotly_chart(
        grafico_processos_por_diretoria(dados),
        use_container_width=True
    )

with col_dep:
    st.plotly_chart(
        grafico_processos_por_departamento(dados, top_n=15),
        use_container_width=True
    )


st.divider()


st.subheader("Demandas")

col_grupo, col_demanda = st.columns(2)

with col_grupo:
    st.plotly_chart(
        grafico_grupos_demanda(dados, top_n=15),
        use_container_width=True
    )

with col_demanda:
    st.plotly_chart(
        grafico_demandas_detalhadas(dados, top_n=20),
        use_container_width=True
    )


st.divider()


st.subheader("Hierarquia analítica")

st.plotly_chart(
    grafico_treemap_hierarquia(dados),
    use_container_width=True
)


st.divider()


st.subheader("Eficiência e tempo")

st.plotly_chart(
    grafico_tempo_medio_por_diretoria(dados),
    use_container_width=True
)


st.divider()


st.subheader("Base analítica")

colunas_base = [
    "numero_processo",
    "data_entrada_novacap",
    "ra_origem",
    "diretoria",
    "departamento",
    "grupo_demanda",
    "demanda",
    "status_atual",
    "categoria_status",
    "dias_tramitacao",
]

st.dataframe(
    dados[colunas_base],
    use_container_width=True,
    hide_index=True
)
