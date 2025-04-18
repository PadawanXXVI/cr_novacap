import os
from dotenv import load_dotenv

# 🔒 Carrega as variáveis de ambiente antes de tudo
load_dotenv()

from flask import Flask
from .ext import db, migrate

def create_app():
    app = Flask(__name__)

    # 🔧 Configurações a partir das variáveis do .env
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 🚀 Inicializa as extensões
    db.init_app(app)
    migrate.init_app(app, db)

    # 📦 Registro de Blueprints (futuro)
    # from app.routes.exemplo import exemplo_bp
    # app.register_blueprint(exemplo_bp)

    return app
