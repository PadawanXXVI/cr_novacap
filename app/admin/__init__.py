# app/admin/__init__.py
"""
Blueprint do módulo Administrativo (Admin) — CR-NOVACAP.

Responsável por rotas de:
- Painel de usuários
- Aprovação, bloqueio/desbloqueio
- Elevação para admin

Observação:
O prefixo de URL (/admin) é aplicado no app/__init__.py
ao registrar o blueprint, então NÃO definimos url_prefix aqui.
"""

from flask import Blueprint

# Nome do blueprint: admin_bp (consistente com as importações e registros)
admin_bp = Blueprint(
    'admin_bp',
    __name__,  # raiz do pacote 'app.admin'
    # Não precisamos apontar template_folder/static_folder aqui:
    # o Flask já procura em app/templates e app/static por padrão.
)

# Importa as rotas para registrar as views no blueprint
from app.admin import routes  # noqa: E402,F401
