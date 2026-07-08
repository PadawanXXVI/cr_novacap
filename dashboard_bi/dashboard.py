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
    grafico_top_ras,
    grafico_grupos_demanda,
    grafico_demandas_detalhadas,
    grafico_tempo_medio_por_diretoria,
)
from mapas import grafico_mapa_ras
from componentes import (
    carregar_css,
    renderizar_cabecalho,
    renderizar_titulo_painel,
    renderizar_rodape,
)


st.set_page_config(
    page_title="Dashboard CR/NOVACAP",
    layout="wide"
)

carregar_css()

st.markdown(
    """
    <script>
        document.documentElement.lang = "pt-BR";
    </script>
    """,
    unsafe_allow_html=True
)


df = carregar_dados()

dados, filtros = aplicar_filtros_sidebar(df)
dados = adicionar_categoria_status(dados)


renderizar_cabecalho()

renderizar_titulo_painel(
    rotulo_periodo=filtros["rotulo_periodo"],
    periodo_formatado=filtros["periodo_formatado"],
)


st.subheader("Indicadores gerais")
exibir_kpis(dados)


st.divider()


st.subheader("Distribuição territorial")

st.plotly_chart(
    grafico_mapa_ras(dados),
    use_container_width=True
)

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

st.plotly_chart(
    grafico_processos_por_diretoria(dados),
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
    "grupo_demanda",
    "demanda",
    "status_atual",
    "categoria_status",
    "dias_ra_ate_novacap",
    "dias_tramitacao",
]

st.dataframe(
    dados[colunas_base],
    use_container_width=True,
    hide_index=True
)


renderizar_rodape()
