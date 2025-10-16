# app/main/_init_.py
"""
Inicialização do módulo principal (Main) — CR-NOVACAP.

Responsável por:
- Tela inicial (index)
- Login e autenticação
- Cadastro e redefinição de senha
- Logout de sessão

💡 Observação:
Este blueprint é o ponto de entrada do sistema e, portanto,
não precisa de prefixo (url_prefix), sendo acessado diretamente.
"""

from flask import Blueprint

# ==========================================================
# 🔷 Criação do Blueprint principal
# ==========================================================
main_bp = Blueprint(
    'main_bp',
    _name_,
    template_folder='../templates',
    static_folder='../static'
)

# ==========================================================
# 🔁 Importação das rotas
# ==========================================================
from app.main import routes  # noqa: E402,F401