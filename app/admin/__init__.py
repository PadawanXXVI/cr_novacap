# app/admin/_init_.py
"""
Inicialização do módulo Administrativo (Admin) — CR-NOVACAP.

Responsável por rotas de:
- Painel de usuários
- Aprovação, bloqueio/desbloqueio
- Elevação e remoção de privilégios administrativos

💡 Observação:
O prefixo /admin é definido diretamente aqui no blueprint para
padronizar com os demais módulos.
"""

from flask import Blueprint

# ==========================================================
# 🔷 Criação do Blueprint
# ==========================================================
admin_bp = Blueprint(
    'admin_bp',
    __name__,
    template_folder='../templates',
    static_folder='../static',
    url_prefix='/admin'
)

# ==========================================================
# 🔁 Importação das rotas
# ==========================================================
from app.admin import routes  # noqa: E402,F401