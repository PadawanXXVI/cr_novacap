from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    # Carrega variáveis de ambiente
    load_dotenv()

    app = Flask(__name__)

    # Configuração a partir do arquivo .env
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa extensões
    db.init_app(app)
    migrate.init_app(app, db)

    # Importa e registra blueprints (rotas)
    # from app.routes.exemplo import exemplo_bp
    # app.register_blueprint(exemplo_bp)

    return app
