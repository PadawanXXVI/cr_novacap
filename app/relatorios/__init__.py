# app/relatorios/__init__.py
"""
Blueprint de Relatórios — CR-NOVACAP.
Gerencia relatórios gerenciais, avançados e exportações.
"""
from flask import Blueprint

relatorios_bp = Blueprint('relatorios_bp', __name__)

from app.relatorios import routes  # noqa: E402,F401
