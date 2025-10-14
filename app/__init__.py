import os
from dotenv import load_dotenv
from flask import Flask
from flask_wtf.csrf import CSRFProtect

# 🔒 Carrega variáveis de ambiente do .env
load_dotenv()

# 🔧 Extensões principais
from app.ext import db, migrate, login_manager
from app.models.modelos import Usuario

# 🔧 Importa os Blueprints
from app.main.routes import main_bp
from app.processos.routes import processos_bp
from app.protocolo.routes import protocolo_bp
from app.relatorios.routes import relatorios_bp
from app.admin.routes import admin_bp


def create_app():
    """Factory principal do sistema CR-NOVACAP"""
    app = Flask(__name__)

    # ============================================================
    # ⚙️ Configurações do Flask e Banco de Dados
    # ============================================================
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # sessão expira em 1h

    # ============================================================
    # 🚀 Inicialização das Extensões
    # ============================================================
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf = CSRFProtect(app)  # proteção contra CSRF nos formulários

    # ============================================================
    # 🔐 Configuração do Flask-Login
    # ============================================================
    login_manager.login_view = 'main_bp.login'
    login_manager.login_message = "Por favor, faça login para acessar esta página."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # ============================================================
    # 📦 Registro de Blueprints
    # ============================================================
    app.register_blueprint(main_bp)
    app.register_blueprint(processos_bp, url_prefix='/processos')
    app.register_blueprint(protocolo_bp, url_prefix='/protocolo')
    app.register_blueprint(relatorios_bp, url_prefix='/relatorios')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # ============================================================
    # 🔁 Rota padrão (caso alguém acesse raiz)
    # ============================================================
    @app.route('/')
    def home_redirect():
        return "<script>window.location.href='/login';</script>"

    return app
