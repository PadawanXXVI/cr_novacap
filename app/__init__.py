# app/__init__.py
import os
from datetime import timedelta, datetime
from dotenv import load_dotenv
from flask import Flask, redirect, url_for

# 🔒 Carrega variáveis de ambiente do .env
load_dotenv()

# 🔧 Extensões principais
from app.ext import db, migrate, login_manager, csrf
from app.models.modelos import Usuario

# ============================================================
# 🔧 Importação dos Blueprints (melhor prática)
# ============================================================
from app.main import main_bp
from app.processos import processos_bp
from app.protocolo import protocolo_bp
from app.relatorios import relatorios_bp
from app.admin import admin_bp


# ============================================================
# 🏗️ Factory principal do sistema CR-NOVACAP
# ============================================================
def create_app():
    app = Flask(__name__)

    # ------------------------------------------------------------
    # ⚙️ Configurações principais
    # ------------------------------------------------------------
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave-secreta-padrao')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

    # ------------------------------------------------------------
    # 🚀 Inicialização das Extensões
    # ------------------------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # ------------------------------------------------------------
    # 🔐 Configuração do Flask-Login
    # ------------------------------------------------------------
    login_manager.login_view = 'main_bp.login'
    login_manager.login_message = "Por favor, faça login para acessar esta página."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        """Carrega o usuário logado na sessão"""
        return Usuario.query.get(int(user_id))

    # ------------------------------------------------------------
    # 📦 Registro de Blueprints
    # ------------------------------------------------------------
    app.register_blueprint(main_bp)
    app.register_blueprint(processos_bp, url_prefix='/processos')
    app.register_blueprint(protocolo_bp, url_prefix='/protocolo')
    app.register_blueprint(relatorios_bp, url_prefix='/relatorios')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # ------------------------------------------------------------
    # 🔁 Rota padrão (redireciona para login)
    # ------------------------------------------------------------
    @app.route('/')
    def home_redirect():
        return redirect(url_for('main_bp.login'))

    # ------------------------------------------------------------
    # 📅 Context Processor (ano atual no rodapé)
    # ------------------------------------------------------------
    @app.context_processor
    def inject_year():
        return {'current_year': datetime.now().year}

    return app
