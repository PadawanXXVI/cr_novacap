# app/processos/__init__.py
"""
Inicialização do módulo de Processos (Tramitação SEI) — CR-NOVACAP.
Define o Blueprint principal do módulo e importa as rotas.
"""

from flask import Blueprint

# Criação do Blueprint
processos_bp = Blueprint(
    'processos_bp',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

# Importa as rotas do módulo
from app.processos import routes
