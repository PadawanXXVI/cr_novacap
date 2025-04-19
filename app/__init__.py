import os
from dotenv import load_dotenv

# 🔒 Carrega variáveis do .env antes de tudo
load_dotenv()

from flask import Flask
from .ext import db, migrate, login_manager  # agora inclui o login_manager
from app.models.modelos import Usuario  # necessário para o user_loader funcionar

def create_app():
    app = Flask(__name__)

    # 🔧 Configurações do Flask
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 🚀 Inicialização de extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # 🔐 Configuração do Flask-Login
    login_manager.login_view = 'login'  # rota usada se o usuário não estiver logado

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # 📦 Registro de Blueprints (futuro)
    # from app.routes.exemplo import exemplo_bp
    # app.register_blueprint(exemplo_bp)

    return app
