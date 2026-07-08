# dashboard_bi/graficos.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


TEMPLATE = "plotly_white"


def figura_vazia(titulo="Sem dados disponíveis"):
    fig = go.Figure()
    fig.update_layout(
        title=titulo,
        template=TEMPLATE,
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": "Nenhum dado encontrado para os filtros selecionados.",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16},
            }
        ],
    )
    return fig


def grafico_evolucao_mensal(df):
    if df.empty:
        return figura_vazia("Evolução mensal dos processos")

    dados = (
        df.groupby("mes_ano")["id_processo"]
        .nunique()
        .reset_index(name="total")
        .sort_values("mes_ano")
    )

    fig = px.line(
        dados,
        x="mes_ano",
        y="total",
        markers=True,
        title="Evolução mensal dos processos",
        template=TEMPLATE,
    )

    fig.update_layout(
        xaxis_title="Mês",
        yaxis_title="Total de processos",
    )

    return fig


def grafico_rosca_status(df):
    if df.empty or "categoria_status" not in df.columns:
        return figura_vazia("Distribuição gerencial por status")

    dados = (
        df.groupby("categoria_status")["id_processo"]
        .nunique()
        .reset_index(name="total")
        .sort_values("total", ascending=False)
    )

    fig = px.pie(
        dados,
        names="categoria_status",
        values="total",
        hole=0.55,
        title="Distribuição gerencial por status",
        template=TEMPLATE,
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
    )

    return fig


def grafico_status_detalhado(df):
    if df.empty:
        return figura_vazia("Processos por status atual")

    dados = (
        df.groupby("status_atual")["id_processo"]
        .nunique()
        .reset_index(name="total")
        .sort_values("total", ascending=True)
    )

    fig = px.bar(
        dados,
        x="total",
        y="status_atual",
        orientation="h",
        title="Processos por status atual",
        template=TEMPLATE,
    )

    fig.update_layout(
        xaxis_title="Total de processos",
        yaxis_title="Status atual",
    )

    return fig


def grafico_processos_por_diretoria(df):
    if df.empty:
        return figura_vazia("Processos por diretoria")

    dados = (
        df.groupby("diretoria")["id_processo"]
        .nunique()
        .reset_index(name="total")
        .sort_values("total", ascending=True)
    )

    fig = px.bar(
        dados,
        x="total",
        y="diretoria",
        orientation="h",
        title="Processos por diretoria",
        template=TEMPLATE,
    )

    fig.update_layout(
        xaxis_title="Total de processos",
        yaxis_title="Diretoria",
    )

    return fig


def grafico_processos_por_departamento(df, top_n=15):
    if df.empty:
        return figura_vazia("Processos por departamento")

    dados = (
        df.groupby("departamento")["id_processo"]
        .nunique()
        .reset_index(name="total")
        .sort_values("total", ascending=True)
        .tail(top_n)
    )

    fig = px.bar(
        dados,
        x="total",
        y="departamento",
        orientation="h",
        title=f"Top {top_n} departamentos por processos",
        template=TEMPLATE,
    )

    fig.update_layout(
        xaxis_title="Total de processos",
        yaxis_title="Departamento",
    )

    return fig


def grafico_top_ras(df, top_n=15):
    if df.empty:
        return figura_vazia("Top RAs por quantidade de processos")

    dados = (
        df.groupby("ra_origem")["id_processo"]
        .nunique()
        .reset_index(name="total")
        .sort_values("total", ascending=True)
        .tail(top_n)
    )

    fig = px.bar(
        dados,
        x="total",
        y="ra_origem",
        orientation="h",
        title=f"Top {top_n} RAs por quantidade de processos",
        template=TEMPLATE,
    )

    fig.update_layout(
        xaxis_title="Total de processos",
        yaxis_title="Região Administrativa",
    )

    return fig


def grafico_grupos_demanda(df, top_n=15):
    if df.empty:
        return figura_vazia("Top grupos de demanda")

    dados = (
        df.groupby("grupo_demanda")["id_processo"]
        .nunique()
        .reset_index(name="total")
        .sort_values("total", ascending=True)
        .tail(top_n)
    )

    fig = px.bar(
        dados,
        x="total",
        y="grupo_demanda",
        orientation="h",
        title=f"Top {top_n} grupos de demanda",
        template=TEMPLATE,
    )

    fig.update_layout(
        xaxis_title="Total de processos",
        yaxis_title="Grupo da demanda",
    )

    return fig


def grafico_demandas_detalhadas(df, top_n=20):
    if df.empty:
        return figura_vazia("Top demandas detalhadas")

    dados = (
        df.groupby("demanda")["id_processo"]
        .nunique()
        .reset_index(name="total")
        .sort_values("total", ascending=True)
        .tail(top_n)
    )

    fig = px.bar(
        dados,
        x="total",
        y="demanda",
        orientation="h",
        title=f"Top {top_n} demandas detalhadas",
        template=TEMPLATE,
    )

    fig.update_layout(
        xaxis_title="Total de processos",
        yaxis_title="Demanda detalhada",
    )

    return fig


def grafico_treemap_hierarquia(df):
    if df.empty:
        return figura_vazia("Hierarquia Diretoria → Departamento → Demanda")

    dados = df.copy()

    dados["diretoria"] = dados["diretoria"].fillna("Não informada")
    dados["departamento"] = dados["departamento"].fillna("Não informado")
    dados["grupo_demanda"] = dados["grupo_demanda"].fillna("Não informado")
    dados["demanda"] = dados["demanda"].fillna("Não informada")

    agrupado = (
        dados.groupby(
            ["diretoria", "departamento", "grupo_demanda", "demanda"]
        )["id_processo"]
        .nunique()
        .reset_index(name="total")
    )

    fig = px.treemap(
        agrupado,
        path=["diretoria", "departamento", "grupo_demanda", "demanda"],
        values="total",
        title="Hierarquia: Diretoria → Departamento → Grupo → Demanda",
        template=TEMPLATE,
    )

    return fig


def grafico_tempo_medio_por_diretoria(df):
    if df.empty or "dias_tramitacao" not in df.columns:
        return figura_vazia("Tempo médio por diretoria")

    dados = (
        df.groupby("diretoria")["dias_tramitacao"]
        .mean()
        .reset_index(name="tempo_medio")
        .sort_values("tempo_medio", ascending=True)
    )

    fig = px.bar(
        dados,
        x="tempo_medio",
        y="diretoria",
        orientation="h",
        title="Tempo médio de tramitação por diretoria",
        template=TEMPLATE,
    )

    fig.update_layout(
        xaxis_title="Tempo médio em dias",
        yaxis_title="Diretoria",
    )

    return fig
