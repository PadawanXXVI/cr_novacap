# dashboard_bi/indicadores.py

import pandas as pd
import streamlit as st


CATEGORIAS_STATUS = {
    # ✅ Atendidos
    "Atendido": "Atendidos",

    # ⏳ Em tramitação
    "Enviado à Diretoria das Cidades": "Em tramitação",
    "Enviado à Diretoria de Obras": "Em tramitação",
    "Enviado à Diretoria de Planejamento e Projetos": "Em tramitação",
    "Enviado à Diretoria de Suporte": "Em tramitação",
    "Solicitação de urgência": "Em tramitação",
    "Solicitação de prazo de execução": "Em tramitação",

    # ↩️ Devolvidos à RA
    "Devolvido à RA de origem – adequação de requisitos": "Devolvidos à RA",
    "Devolvido à RA de origem – implantação": "Devolvidos à RA",
    "Devolvido à RA de origem – parecer técnico de outro órgão": "Devolvidos à RA",
    "Devolvido à RA de origem – serviço com contrato de natureza continuada pela DC/DO": "Devolvidos à RA",
    "Devolvido à RA de origem – parceria (fornecimento de recursos pela NOVACAP)": "Devolvidos à RA",
    "Devolvido à RA de origem – solicitação de fonte orçamentária": "Devolvidos à RA",

    # ❌ Improcedentes
    "Improcedente – tramitação via SGIA": "Improcedentes",
    "Improcedente – tramita por órgão diferente da NOVACAP": "Improcedentes",
    "Improcedente – tramitação via SGMV": "Improcedentes",

    # 🏁 Encerrados pela RA
    "Encerrado pela RA de origem": "Encerrados pela RA",

    # 📞 Ouvidoria
    "Processo oriundo de Ouvidoria": "Ouvidoria",
}


def classificar_status(status):
    if pd.isna(status):
        return "Não informado"

    status = str(status).strip()
    return CATEGORIAS_STATUS.get(status, "Outros")


def adicionar_categoria_status(df):
    df = df.copy()

    if "status_atual" not in df.columns:
        df["categoria_status"] = "Não informado"
        return df

    df["categoria_status"] = df["status_atual"].apply(classificar_status)
    return df


def contar_categoria(df, categoria):
    return df.loc[
        df["categoria_status"] == categoria,
        "id_processo"
    ].nunique()


def calcular_kpis(df):
    if df.empty:
        return {
            "total_processos": 0,
            "atendidos": 0,
            "em_tramitacao": 0,
            "devolvidos": 0,
            "encerrados_ra": 0,
            "improcedentes": 0,
            "ouvidoria": 0,
            "outros": 0,
        }

    df = adicionar_categoria_status(df)

    return {
        "total_processos": df["id_processo"].nunique(),
        "atendidos": contar_categoria(df, "Atendidos"),
        "em_tramitacao": contar_categoria(df, "Em tramitação"),
        "devolvidos": contar_categoria(df, "Devolvidos à RA"),
        "encerrados_ra": contar_categoria(df, "Encerrados pela RA"),
        "improcedentes": contar_categoria(df, "Improcedentes"),
        "ouvidoria": contar_categoria(df, "Ouvidoria"),
        "outros": contar_categoria(df, "Outros"),
    }


def exibir_kpis(df):
    indicadores = calcular_kpis(df)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📁 Total de processos", indicadores["total_processos"])
    col2.metric("⏳ Em tramitação", indicadores["em_tramitacao"])
    col3.metric("✅ Atendidos", indicadores["atendidos"])
    col4.metric("↩️ Devolvidos à RA", indicadores["devolvidos"])

    col5, col6, col7, col8 = st.columns(4)

    col5.metric("🏁 Encerrados pela RA", indicadores["encerrados_ra"])
    col6.metric("❌ Improcedentes", indicadores["improcedentes"])
    col7.metric("📞 Ouvidoria", indicadores["ouvidoria"])
    col8.metric("📌 Outros", indicadores["outros"])

    return indicadores
