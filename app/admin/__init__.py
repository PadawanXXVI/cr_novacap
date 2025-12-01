# app/admin/__init__.py
"""
Inicialização do módulo Administrativo (Admin) — CR-NOVACAP.

Responsável por rotas de:
- Painel de usuários
- Aprovação, bloqueio/desbloqueio
- Elevação e remoção de privilégios administrativos

💡 Observação:
O prefixo /admin é definido NO app/__init__.py,
portanto NÃO deve ser definido aqui no Blueprint.
"""

from flask import Blueprint

# ==========================================================
# 🔷 Criação do Blueprint (SEM url_prefix)
# ==========================================================
admin_bp = Blueprint(
    'admin_bp',
    __name__,
    template_folder='templates',   # caminho correto relativo ao pacote
    static_folder='static'
)

# ==========================================================
# 🔁 Importação das rotas
# ==========================================================
from app.admin import routes  # noqa: E402,F401
