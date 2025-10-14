# app/protocolo/__init__.py
"""
Inicialização do módulo de Protocolo (CRM de Atendimentos) — CR-NOVACAP.
Define o Blueprint do módulo e importa as rotas.
"""

from flask import Blueprint

# Cria o Blueprint
protocolo_bp = Blueprint(
    'protocolo_bp',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

# Importa as rotas do módulo
from app.protocolo import routes
