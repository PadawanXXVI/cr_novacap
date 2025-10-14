# app/admin/__init__.py
"""
Blueprint do módulo administrativo — CR-NOVACAP.
Gerencia aprovação de usuários, bloqueios e permissões de administrador.
"""
from flask import Blueprint

admin_bp = Blueprint('admin_bp', __name__)

from app.admin import routes  # noqa: E402,F401
