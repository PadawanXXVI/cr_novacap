import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

# Carregar variáveis do .env
load_dotenv()

# Configurar logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "atualiza_mmd.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def conectar_banco(database_url):
    try:
        engine = create_engine(database_url)
        logging.info(f"Conectado ao banco: {database_url}")
        return engine
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco: {e}")
        raise

def atualizar_dimensoes(engine_origem, engine_mmd):
    try:
        # Atualizar dimensão região
        df_regiao = pd.read_sql("SELECT id AS id_regiao, nome AS nome_regiao FROM regioes_administrativas", engine_origem)
        df_regiao.to_sql("dim_regiao", con=engine_mmd, if_exists="replace", index=False)
        logging.info(f"Tabela 'dim_regiao' atualizada com {len(df_regiao)} registros.")

        # Atualizar tabela fato_processos (exemplo simplificado)
        df_fato = pd.read_sql("""
            SELECT 
                id AS id_processo,
                id_regiao,
                id_tipo,
                data_entrada
            FROM entradas_processo
        """, engine_origem)
        df_fato.to_sql("fato_processos", con=engine_mmd, if_exists="replace", index=False)
        logging.info(f"Tabela 'fato_processos' atualizada com {len(df_fato)} registros.")

    except Exception as e:
        logging.error(f"Erro ao atualizar tabelas: {e}")
        raise

def main():
    logging.info("🔁 Iniciando atualização do MMD.")
    try:
        origem_url = os.getenv("DATABASE_ORIGEM")
        destino_url = os.getenv("DATABASE_DESTINO")

        engine_origem = conectar_banco(origem_url)
        engine_mmd = conectar_banco(destino_url)

        atualizar_dimensoes(engine_origem, engine_mmd)

        logging.info("✅ Atualização do MMD concluída com sucesso.")

    except Exception as e:
        logging.error(f"❌ Erro geral na execução: {e}")

if __name__ == "__main__":
    main()
