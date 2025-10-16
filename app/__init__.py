# app/_init_.py
"""
Inicialização principal do sistema CR-NOVACAP — Controle de Processos e Atendimentos.
Configurações globais, registro de extensões e blueprints institucionais.
"""

import os
from datetime import timedelta, datetime
from dotenv import load_dotenv
from flask import Flask, redirect, url_for

# ==========================================================
# 🔒 Carrega variáveis de ambiente
# ==========================================================
load_dotenv()

# ==========================================================
# ⚙ Extensões principais
# ==========================================================
from app.ext import db, migrate, login_manager, csrf
from app.models.modelos import Usuario

# ==========================================================
# 📦 Importação dos Blueprints
# ==========================================================
from app.main import main_bp
from app.processos import processos_bp
from app.protocolo import protocolo_bp
from app.relatorios import relatorios_bp
from app.admin import admin_bp


# ==========================================================
# 🏗 Factory principal do sistema CR-NOVACAP
# ==========================================================
def create_app():
    """Cria e configura a aplicação Flask principal."""
    app = Flask(_name_)

    # ------------------------------------------------------
    # 🔧 Configurações básicas do sistema
    # ------------------------------------------------------
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'chave-secreta-padrao'),
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
    )

    # ------------------------------------------------------
    # 🚀 Inicialização das extensões
    # ------------------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # ------------------------------------------------------
    # 🔐 Configuração de autenticação (Flask-Login)
    # ------------------------------------------------------
    login_manager.login_view = 'main_bp.login'
    login_manager.login_message = "Por favor, faça login para acessar esta página."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        """Carrega o usuário autenticado na sessão."""
        return Usuario.query.get(int(user_id))

    # ------------------------------------------------------
    # 📦 Registro de Blueprints institucionais
    # (cada módulo já define seu url_prefix internamente)
    # ------------------------------------------------------
    app.register_blueprint(main_bp)
    app.register_blueprint(processos_bp)
    app.register_blueprint(protocolo_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(admin_bp)

    # ------------------------------------------------------
    # 🏠 Rota padrão (redireciona para login)
    # ------------------------------------------------------
    @app.route('/')
    def home_redirect():
        return redirect(url_for('main_bp.login'))

    # ------------------------------------------------------
    # 📅 Contexto global (ano atual no rodapé)
    # ------------------------------------------------------
    @app.context_processor
    def inject_year():
        """Adiciona o ano atual ao contexto global."""
        return {'current_year': datetime.now().year}

    return app
