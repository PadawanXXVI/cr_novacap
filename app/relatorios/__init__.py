# app/relatorios/_init_.py
"""
Inicialização do módulo de Relatórios — CR-NOVACAP.

Responsável por:
- Relatórios gerenciais e operacionais
- Exportações em PDF, CSV e XLSX
- Indicadores de desempenho por diretoria e tipo de atendimento

💡 Observação:
O prefixo /relatorios é definido automaticamente no app/_init_.py
durante o registro do blueprint.
"""

from flask import Blueprint

# ==========================================================
# 🟨 Criação do Blueprint principal do módulo
# ==========================================================
relatorios_bp = Blueprint(
    'relatorios_bp',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

# ==========================================================
# 🔁 Importação das rotas (mantida ao final)
# ==========================================================
from app.relatorios import routes  # noqa: E402,F401
