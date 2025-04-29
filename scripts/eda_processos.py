# Análise de Dados dos Processos – CR/NOVACAP

# 📦 Carregar bibliotecas
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import plotly.express as px

# 🔐 Conectar usando o .env
load_dotenv()
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

# 📥 Carregar dados da VIEW
df = pd.read_sql("SELECT * FROM vw_processos_completos", con=engine)
print("\n📌 Primeiros registros da view:")
print(df.head())

# 📊 Análises básicas
print("\n📈 Informações gerais:")
print(df.info())

print("\n📊 Quantidade por status final:")
print(df['status_final'].value_counts())

print("\n📍 Quantidade por Região Administrativa:")
print(df['ra_origem'].value_counts())

# 🗓️ Processos por mês de entrada na Novacap
df['data_entrada_novacap'] = pd.to_datetime(df['data_entrada_novacap'])
df['mes_ano'] = df['data_entrada_novacap'].dt.to_period('M').astype(str)
print("\n📅 Processos por mês:")
print(df['mes_ano'].value_counts().sort_index())

# 📈 Gráficos com Plotly
fig1 = px.bar(df, x='ra_origem', title='Processos por Região Administrativa (RA)', labels={'ra_origem': 'Região Administrativa'})
fig1.show()

fig2 = px.histogram(df, x='status_final', title='Distribuição por Status Final', labels={'status_final': 'Status'})
fig2.show()

# 📤 Exportar para Excel
df.to_excel("analise_processos.xlsx", index=False)
print("\n✅ Arquivo 'analise_processos.xlsx' salvo com sucesso.")
