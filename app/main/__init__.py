# app/main/__init__.py
"""
Inicialização do módulo principal (Main) — CR-NOVACAP.
Define o Blueprint principal usado para login, cadastro, tela inicial e logout.
"""

from flask import Blueprint

# Cria o Blueprint principal
main_bp = Blueprint(
    'main_bp',
    __name__,
    template_folder='../templates',   # garante acesso às páginas HTML
    static_folder='../static'         # garante acesso aos arquivos CSS/JS
)

# Importa as rotas associadas ao Blueprint
from app.main import routes
