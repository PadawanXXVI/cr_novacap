# dashboard_bi/indicadores.py

import pandas as pd
import streamlit as st


CATEGORIAS_STATUS = {
    "Atendido": "Atendidos",
    "Encerrado pela RA de origem": "Atendidos",

    "Enviado à Diretoria das Cidades": "Em tramitação",
    "Enviado à Diretoria de Obras": "Em tramitação",
    "Enviado à Diretoria de Planejamento e Projetos": "Em tramitação",
    "Enviado à Diretoria de Suporte": "Em tramitação",
    "Solicitação de urgência": "Em tramitação",
    "Solicitação de prazo de execução": "Em tramitação",

    "Devolvido à RA de origem – adequação de requisitos": "Devolvidos à RA",
    "Devolvido à RA de origem – implantação": "Devolvidos à RA",
    "Devolvido à RA de origem – parecer técnico de outro órgão": "Devolvidos à RA",
    "Devolvido à RA de origem – serviço com contrato de natureza continuada pela DC/DO": "Devolvidos à RA",

    "Improcedente – tramitação via SGIA": "Improcedentes",
    "Improcedente – tramita por órgão diferente da NOVACAP": "Improcedentes",

    "Processo oriundo de Ouvidoria": "Ouvidoria",
}


def classificar_status(status):
    if pd.isna(status):
        return "Não informado"

    status = str(status).strip()

    if status in CATEGORIAS_STATUS:
        return CATEGORIAS_STATUS[status]

    return "Outros"


def adicionar_categoria_status(df):
    df = df.copy()

    if "status_atual" not in df.columns:
        df["categoria_status"] = "Não informado"
        return df

    df["categoria_status"] = df["status_atual"].apply(classificar_status)

    return df


def calcular_kpis(df):
    if df.empty:
        return {
            "total_processos": 0,
            "atendidos": 0,
            "em_tramitacao": 0,
            "devolvidos": 0,
            "improcedentes": 0,
            "ouvidoria": 0,
        }

    df = adicionar_categoria_status(df)

    return {
        "total_processos": df["id_processo"].nunique(),
        "atendidos": df.loc[df["categoria_status"] == "Atendidos", "id_processo"].nunique(),
        "em_tramitacao": df.loc[df["categoria_status"] == "Em tramitação", "id_processo"].nunique(),
        "devolvidos": df.loc[df["categoria_status"] == "Devolvidos à RA", "id_processo"].nunique(),
        "improcedentes": df.loc[df["categoria_status"] == "Improcedentes", "id_processo"].nunique(),
        "ouvidoria": df.loc[df["categoria_status"] == "Ouvidoria", "id_processo"].nunique(),
    }


def exibir_kpis(df):
    indicadores = calcular_kpis(df)

    col1, col2, col3 = st.columns(3)

    col1.metric("📁 Total de processos", indicadores["total_processos"])
    col2.metric("✅ Atendidos", indicadores["atendidos"])
    col3.metric("⏳ Em tramitação", indicadores["em_tramitacao"])

    col4, col5, col6 = st.columns(3)

    col4.metric("↩️ Devolvidos à RA", indicadores["devolvidos"])
    col5.metric("❌ Improcedentes", indicadores["improcedentes"])
    col6.metric("📞 Ouvidoria", indicadores["ouvidoria"])

    return indicadores
