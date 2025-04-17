from flask import Flask
from .ext import db, migrate  # Importa as extensões a partir de ext.py
from dotenv import load_dotenv
import os

def create_app():
    # Carrega variáveis de ambiente do .env
    load_dotenv()

    app = Flask(__name__)

    # Configurações do Flask
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)

    # Aqui você pode registrar blueprints futuramente
    # from app.routes.exemplo import exemplo_bp
    # app.register_blueprint(exemplo_bp)

    return app
