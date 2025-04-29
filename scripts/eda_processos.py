
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

# 📥 Carregar dados da tabela de processos
df = pd.read_sql("SELECT * FROM processos", con=engine)
print("\n📌 Primeiros registros:")
print(df.head())

# 📊 Análises básicas
print("\n📈 Informações gerais:")
print(df.info())

print("\n📊 Quantidade por status:")
print(df['status'].value_counts())

print("\n📍 Quantidade por RA:")
print(df['regiao_administrativa'].value_counts())

# 🗓️ Processos por Mês
df['data_criacao'] = pd.to_datetime(df['data_criacao'])
df['mes_ano'] = df['data_criacao'].dt.to_period('M').astype(str)
print("\n📅 Processos por mês:")
print(df['mes_ano'].value_counts().sort_index())

# 📈 Gráficos
fig1 = px.bar(df, x='regiao_administrativa', title='Processos por Região Administrativa')
fig1.show()

fig2 = px.histogram(df, x='status', title='Distribuição por Status')
fig2.show()

# 📤 Exportar para Excel
df.to_excel("analise_processos.xlsx", index=False)
print("\n✅ Arquivo 'analise_processos.xlsx' salvo com sucesso.")
