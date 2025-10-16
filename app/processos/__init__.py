# app/processos/_init_.py
"""
Inicialização do módulo de Processos (Tramitação SEI) — CR-NOVACAP.
Define o Blueprint principal do módulo e carrega as rotas.
"""

from flask import Blueprint

# ==========================================================
# 🔷 Criação do Blueprint
# ==========================================================
processos_bp = Blueprint(
    'processos_bp',
    __name__,
    template_folder='../templates',
    static_folder='../static',
    url_prefix='/processos'  # 🔗 define o prefixo direto no blueprint
)

# ==========================================================
# 🔁 Importação das rotas
# ==========================================================
# Importar no final evita import circular com app.ext e app.models
from app.processos import routes  # noqa: E402,F401