# app/relatorios/__init__.py
"""
Inicialização do módulo de Relatórios — CR-NOVACAP.
Define o Blueprint do módulo e importa as rotas.
"""

from flask import Blueprint

# Criação do Blueprint
relatorios_bp = Blueprint(
    'relatorios_bp',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

# Importa as rotas do módulo
from app.relatorios import routes
