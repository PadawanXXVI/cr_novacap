import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Carregar dados
df = pd.read_excel("analise_processos.xlsx")
df['data_entrada_novacap'] = pd.to_datetime(df['data_entrada_novacap'], errors='coerce')
df['mes_ano'] = df['data_entrada_novacap'].dt.to_period('M').astype(str)

# Inicializar app com tema LUX
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = "Painel de BI - CR/NOVACAP"

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Painel de BI - CR/NOVACAP", className="text-center text-primary mt-4 mb-4"), width=12)
    ]),

    # KPIs
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Total de Processos"),
            dbc.CardBody(html.H4(f"{len(df)}", className="text-center"))
        ], color="primary", inverse=True), md=3),

        dbc.Col(dbc.Card([
            dbc.CardHeader("RAs distintas"),
            dbc.CardBody(html.H4(f"{df['ra_origem'].nunique()}", className="text-center"))
        ], color="info", inverse=True), md=3),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Status únicos"),
            dbc.CardBody(html.H4(f"{df['status_final'].nunique()}", className="text-center"))
        ], color="secondary", inverse=True), md=3),

        dbc.Col(dbc.Card([
            dbc.CardHeader("Última entrada"),
            dbc.CardBody(html.H4(df['data_entrada_novacap'].max().strftime('%d/%m/%Y'), className="text-center"))
        ], color="dark", inverse=True), md=3),
    ], className="mb-4"),

    # Filtros
    dbc.Row([
        dbc.Col([
            html.Label("Região Administrativa", className="fw-bold"),
            dcc.Dropdown(
                options=[{'label': ra, 'value': ra} for ra in sorted(df['ra_origem'].dropna().unique())],
                id='filtro-ra',
                placeholder="Selecione uma RA"
            )
        ], md=6),
        dbc.Col([
            html.Label("Status Final", className="fw-bold"),
            dcc.Dropdown(
                options=[{'label': s, 'value': s} for s in sorted(df['status_final'].dropna().unique())],
                id='filtro-status',
                placeholder="Selecione o Status"
            )
        ], md=6),
    ], className="mb-4"),

    # Gráficos
    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico_ra'), md=12),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico_status'), md=6),
        dbc.Col(dcc.Graph(id='grafico_mensal'), md=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id='grafico_calor'), md=12),
    ])
], fluid=True)

# Callback dos gráficos
@app.callback(
    Output('grafico_ra', 'figure'),
    Output('grafico_status', 'figure'),
    Output('grafico_mensal', 'figure'),
    Output('grafico_calor', 'figure'),
    Input('filtro-ra', 'value'),
    Input('filtro-status', 'value')
)
def atualizar_graficos(ra, status):
    dados = df.copy()
    if ra:
        dados = dados[dados['ra_origem'] == ra]
    if status:
        dados = dados[dados['status_final'] == status]

    fig_ra = px.bar(dados, x='ra_origem', title="Processos por RA", template='plotly_white')
    fig_status = px.histogram(dados, x='status_final', title="Distribuição por Status Final", template='plotly_white')
    fig_mensal = px.histogram(dados, x='mes_ano', title="Processos por Mês", template='plotly_white')

    # Mapa de calor RA x Status Final
    mapa = dados.groupby(['ra_origem', 'status_final']).size().reset_index(name='qtd')
    fig_calor = px.density_heatmap(
        mapa, x='ra_origem', y='status_final', z='qtd',
        title="Mapa de Calor: RA × Status Final",
        color_continuous_scale='Blues',
        template='plotly_white'
    )

    return fig_ra, fig_status, fig_mensal, fig_calor

# Executar servidor local
if __name__ == '__main__':
    app.run(debug=True)

# --------------------------------------------
# CLI Flask para atualizar MMD manualmente
# --------------------------------------------
from flask import Flask as FlaskCLI
import subprocess

cli_app = FlaskCLI(__name__)

@cli_app.cli.command("atualizar_mmd")
def atualizar_mmd():
    """Atualiza o Modelo Multidimensional com os dados mais recentes do cr_novacap"""
    print("🔄 Iniciando atualização do MMD via script...")
    subprocess.run(["python", "atualiza_mmd.py"])
    print("✅ Atualização concluída com sucesso.")
