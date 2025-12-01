# app/relatorios/__init__.py
"""
Inicialização do módulo de Relatórios — CR-NOVACAP.

Responsável por:
- Relatórios gerenciais e operacionais
- Exportações em PDF, CSV e XLSX
- Indicadores de desempenho por diretoria e tipo de atendimento

💡 Observação:
O prefixo /relatorios é definido exclusivamente no app/__init__.py.
Portanto, NÃO deve ser definido aqui no Blueprint.
"""

from flask import Blueprint

# ==========================================================
# 🟨 Criação do Blueprint (SEM url_prefix)
# ==========================================================
relatorios_bp = Blueprint(
    'relatorios_bp',
    __name__,
    template_folder='templates',   # caminho correto relativo ao pacote
    static_folder='static'
)

# ==========================================================
# 🔁 Importação das rotas
# ==========================================================
from app.relatorios import routes  # noqa: E402,F401
