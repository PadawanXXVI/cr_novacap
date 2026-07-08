# dashboard_bi/consultas.py

import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


@st.cache_resource
def conectar_banco():
    if not DATABASE_URL:
        st.error("DATABASE_URL não encontrada no arquivo .env.")
        st.stop()

    return create_engine(DATABASE_URL)


@st.cache_data(ttl=300)
def carregar_dados():
    engine = conectar_banco()

    query = """
        SELECT
            p.id_processo,
            p.numero_processo,
            p.status_atual,

            COALESCE(
                p.diretoria_destino,
                'Não informada'
            ) AS diretoria,

            p.diretoria_destino,

            e.data_criacao_ra,
            e.data_entrada_novacap,
            e.data_documento,
            e.ra_origem,

            d.descricao AS demanda,

            COALESCE(
                dir.descricao_exibicao,
                dir.nome_completo,
                dir.sigla,
                'Não informada'
            ) AS diretoria_catalogo,

            dir.sigla AS sigla_diretoria_catalogo,
            dir.tipo AS tipo_diretoria_catalogo,
            dir.ordem_exibicao AS ordem_diretoria_catalogo,

            COALESCE(dep.nome, 'Não informado') AS departamento,

            u.usuario AS responsavel

        FROM processos p

        JOIN entradas_processo e
            ON e.id_processo = p.id_processo

        JOIN demandas d
            ON d.id_demanda = e.id_demanda

        LEFT JOIN diretorias dir
            ON dir.id_diretoria = d.id_diretoria

        LEFT JOIN departamentos dep
            ON dep.id_departamento = d.id_departamento

        JOIN usuarios u
            ON u.id_usuario = e.usuario_responsavel

        ORDER BY
            e.data_entrada_novacap ASC,
            p.diretoria_destino ASC
    """

    df = pd.read_sql(query, engine)

    return tratar_dados(df)


def tratar_dados(df):
    if df.empty:
        return df

    colunas_data = [
        "data_criacao_ra",
        "data_entrada_novacap",
        "data_documento",
    ]

    for coluna in colunas_data:
        df[coluna] = pd.to_datetime(df[coluna], errors="coerce")

    df["ano"] = df["data_entrada_novacap"].dt.year
    df["mes"] = df["data_entrada_novacap"].dt.month
    df["mes_nome"] = df["data_entrada_novacap"].dt.strftime("%B")
    df["mes_ano"] = df["data_entrada_novacap"].dt.to_period("M").astype(str)
    df["trimestre"] = df["data_entrada_novacap"].dt.quarter
    df["bimestre"] = ((df["mes"] - 1) // 2) + 1

    df["grupo_demanda"] = (
        df["demanda"]
        .astype(str)
        .str.split(" - ")
        .str[0]
        .str.strip()
    )

    df["diretoria"] = df["diretoria"].fillna("Não informada")
    df["diretoria_destino"] = df["diretoria_destino"].fillna("Não informada")
    df["diretoria_catalogo"] = df["diretoria_catalogo"].fillna("Não informada")
    df["departamento"] = df["departamento"].fillna("Não informado")
    df["status_atual"] = df["status_atual"].fillna("Não informado")
    df["ra_origem"] = df["ra_origem"].fillna("Não informada")
    df["demanda"] = df["demanda"].fillna("Não informada")
    df["grupo_demanda"] = df["grupo_demanda"].fillna("Não informada")

    df["dias_ra_ate_novacap"] = (
        df["data_entrada_novacap"] - df["data_criacao_ra"]
    ).dt.days

    hoje = pd.Timestamp.today().normalize()

    df["dias_tramitacao"] = (
        hoje - df["data_entrada_novacap"]
    ).dt.days

    return df
