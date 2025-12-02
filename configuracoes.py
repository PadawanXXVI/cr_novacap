import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "chave-padrao-insegura")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///cr.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
