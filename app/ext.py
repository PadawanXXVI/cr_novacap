# app/ext.py
"""
Central de extensões do Flask — CR-NOVACAP
Todas as instâncias das extensões Flask ficam aqui,
e são inicializadas em app/__init__.py (create_app()).
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect

# ==========================================================
# 🧱 Instâncias globais de extensões
# ==========================================================

# ORM e Migrations
db = SQLAlchemy()
migrate = Migrate()

# Controle de autenticação
login_manager = LoginManager()

# Proteção contra ataques CSRF em formulários
csrf = CSRFProtect()

# ==========================================================
# 🔧 Observação:
# Todas as extensões são inicializadas dentro da função
# create_app() localizada em app/__init__.py
# Exemplo:
#   from app.ext import db, migrate, login_manager, csrf
#   db.init_app(app)
#   csrf.init_app(app)
# ==========================================================
