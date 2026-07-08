# dashboard_bi/componentes.py

from pathlib import Path
import base64
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
STYLE_PATH = BASE_DIR / "style.css"
ASSETS_DIR = BASE_DIR / "assets"

LOGO_GDF = ASSETS_DIR / "ico-logo-gdf.svg"
LOGO_NOVACAP = ASSETS_DIR / "logo-novacap.png"


def carregar_css():
    if STYLE_PATH.exists():
        with open(STYLE_PATH, "r", encoding="utf-8") as arquivo:
            st.markdown(f"<style>{arquivo.read()}</style>", unsafe_allow_html=True)


def converter_imagem_base64(caminho):
    if not caminho.exists():
        return ""

    extensao = caminho.suffix.replace(".", "").lower()

    if extensao == "svg":
        mime = "image/svg+xml"
    elif extensao == "png":
        mime = "image/png"
    elif extensao in ["jpg", "jpeg"]:
        mime = "image/jpeg"
    else:
        mime = "image/png"

    with open(caminho, "rb") as arquivo:
        conteudo = base64.b64encode(arquivo.read()).decode("utf-8")

    return f"data:{mime};base64,{conteudo}"


def obter_clima_local():
    return {
        "local": "Brasília",
        "icone": "☀️",
        "temperatura": "16°C",
    }


def renderizar_cabecalho():
    logo_gdf = converter_imagem_base64(LOGO_GDF)
    clima = obter_clima_local()

    st.markdown(
        f"""
<div class="cr-header">
    <div class="cr-header-left">
        <img src="{logo_gdf}" class="cr-header-logo" alt="GDF">
        <div>
            <p class="cr-header-title">Companhia Urbanizadora da Nova Capital - NOVACAP</p>
            <p class="cr-header-subtitle">Painel Executivo de Business Intelligence</p>
        </div>
    </div>
    <div class="cr-header-weather">
        <span>{clima["local"]}</span>
        <span>{clima["icone"]}</span>
        <span>{clima["temperatura"]}</span>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def renderizar_titulo_painel(rotulo_periodo, periodo_formatado):
    st.markdown(
        f"""
<div class="cr-title-card">
    <h1>Central de Relacionamento – NOVACAP</h1>
    <p><strong>Análise Gerencial —</strong> {rotulo_periodo}</p>
    <p><strong>Período analisado:</strong> {periodo_formatado}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def renderizar_rodape():
    st.markdown(
        """
<div class="cr-footer">
    <p>Governo do Distrito Federal — Companhia Urbanizadora da Nova Capital do Brasil (NOVACAP)</p>
    <p>Central de Relacionamento — Sistema de Controle de Processos SEI</p>
</div>
        """,
        unsafe_allow_html=True,
    )
