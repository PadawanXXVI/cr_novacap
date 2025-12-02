import os
from dotenv import load_dotenv

# ==================================================
# 📌 Carregamento seguro do arquivo .env
# --------------------------------------------------
# Garante que o Flask SEMPRE leia o .env localizado
# na raiz do projeto, evitando conflitos com .env
# de outras pastas ou variáveis do sistema.
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(dotenv_path=ENV_PATH)

# ==================================================
# ⚙ Configurações principais da aplicação
# ==================================================

class Config:
    # 🔐 Chave de segurança
    SECRET_KEY = os.getenv("SECRET_KEY", "chave-padrao-insegura")

    # 🗄 Conexão com o banco de dados (MySQL remoto)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///cr.db")

    # 🚫 Evita warnings do SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
