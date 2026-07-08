# dashboard_bi/mapas.py

import re
import plotly.express as px
import plotly.graph_objects as go


COORDENADAS_RAS = {
    "Plano Piloto": (-15.7939, -47.8828),
    "Gama": (-16.0207, -48.0619),
    "Taguatinga": (-15.8320, -48.0563),
    "Brazlândia": (-15.6716, -48.2005),
    "Sobradinho": (-15.6500, -47.7920),
    "Planaltina": (-15.6179, -47.6487),
    "Paranoá": (-15.7754, -47.7795),
    "Núcleo Bandeirante": (-15.8713, -47.9669),
    "Ceilândia": (-15.8190, -48.1080),
    "Guará": (-15.8246, -47.9870),
    "Cruzeiro": (-15.7890, -47.9390),
    "Samambaia": (-15.8797, -48.0856),
    "Santa Maria": (-16.0137, -47.9920),
    "São Sebastião": (-15.9016, -47.7727),
    "Recanto das Emas": (-15.9023, -48.0657),
    "Lago Sul": (-15.8420, -47.8720),
    "Riacho Fundo": (-15.8810, -48.0060),
    "Lago Norte": (-15.7260, -47.8660),
    "Candangolândia": (-15.8495, -47.9506),
    "Águas Claras": (-15.8373, -48.0256),
    "Riacho Fundo II": (-15.9087, -48.0500),
    "Sudoeste/Octogonal": (-15.7975, -47.9258),
    "Varjão": (-15.7100, -47.8760),
    "Park Way": (-15.9020, -47.9570),
    "SCIA/Estrutural": (-15.7800, -47.9960),
    "Sobradinho II": (-15.6500, -47.8450),
    "Jardim Botânico": (-15.8697, -47.7992),
    "Itapoã": (-15.7475, -47.7626),
    "SIA": (-15.8035, -47.9658),
    "Vicente Pires": (-15.8050, -48.0200),
    "Fercal": (-15.6000, -47.9000),
    "Sol Nascente/Pôr do Sol": (-15.8150, -48.1350),
    "Arniqueira": (-15.8600, -48.0150),
    "Arapoanga": (-15.6100, -47.6700),
    "Água Quente": (-15.9350, -48.0950),
}


def normalizar_nome_ra(valor):
    if not valor:
        return ""

    nome = str(valor).strip()
    nome = re.sub(r"\s*\(RA\s+[IVXLCDM]+\)", "", nome, flags=re.IGNORECASE)
    return nome.strip()


def figura_mapa_vazio():
    fig = go.Figure()

    fig.update_layout(
        title="Mapa das Regiões Administrativas do DF",
        height=650,
        template="plotly_white",
        annotations=[
            {
                "text": "Nenhuma Região Administrativa encontrada para os filtros selecionados.",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16},
            }
        ],
    )

    return fig


def definir_zoom(dados):
    total_ras = dados["ra_origem"].nunique()

    if total_ras == 1:
        return 11.5

    if total_ras <= 3:
        return 10

    if total_ras <= 8:
        return 9

    return 8.3


def definir_centro(dados):
    return {
        "lat": dados["latitude"].mean(),
        "lon": dados["longitude"].mean(),
    }


def grafico_mapa_ras(df):
    if df.empty or "ra_origem" not in df.columns:
        return figura_mapa_vazio()

    dados = (
        df.groupby("ra_origem")["id_processo"]
        .nunique()
        .reset_index(name="total")
    )

    dados["ra_base"] = dados["ra_origem"].apply(normalizar_nome_ra)

    dados["latitude"] = dados["ra_base"].map(
        lambda nome: COORDENADAS_RAS.get(nome, (None, None))[0]
    )

    dados["longitude"] = dados["ra_base"].map(
        lambda nome: COORDENADAS_RAS.get(nome, (None, None))[1]
    )

    dados = dados.dropna(subset=["latitude", "longitude"])

    if dados.empty:
        return figura_mapa_vazio()

    centro = definir_centro(dados)
    zoom = definir_zoom(dados)

    fig = px.scatter_mapbox(
        dados,
        lat="latitude",
        lon="longitude",
        size="total",
        color="total",
        hover_name="ra_origem",
        hover_data={
            "total": True,
            "latitude": False,
            "longitude": False,
            "ra_base": False,
        },
        size_max=50,
        zoom=zoom,
        center=centro,
        height=680,
        title="Mapa das Regiões Administrativas do DF",
        color_continuous_scale="Blues",
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        margin=dict(l=0, r=0, t=60, b=0),
        coloraxis_colorbar_title="Processos",
    )

    return fig
