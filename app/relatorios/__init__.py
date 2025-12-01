# app/relatorios/__init__.py
"""
Inicialização do módulo de Relatórios — CR-NOVACAP.

Responsável por:
- Relatórios gerenciais simples e avançados
- Painel de BI
- Exportações em PDF, CSV e XLSX
- Indicadores de desempenho por diretoria, status e RA

💡 Importante:
O blueprint DEVE declarar o prefixo URL aqui, diretamente neste arquivo.
A responsabilidade NÃO deve ficar no app/__init__.py.
Isso evita conflitos e garante URLs consistentes:

    /relatorios/gerenciais
    /relatorios/avancados
    /relatorios/exportar
    /relatorios/gerar-sei
    /relatorios/bi

"""

from flask import Blueprint

# ==========================================================
# 🟦 Criação do Blueprint com prefixo correto
# ==========================================================
relatorios_bp = Blueprint(
    "relatorios_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/relatorios"     # 🔥 Prefixo DEFINITIVO e obrigatório
)

# ==========================================================
# 🔁 Importação das rotas (depois do blueprint)
# ==========================================================
from app.relatorios import routes  # noqa: E402,F401
