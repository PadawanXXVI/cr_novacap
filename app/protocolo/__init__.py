# app/protocolo/_init_.py
"""
Inicialização do módulo de Protocolo (CRM de Atendimentos) — CR-NOVACAP.

Responsável por:
- Registro de protocolos de atendimento
- Acompanhamento de interações e status
- Exportação de dados e relatórios relacionados

💡 Observação:
O prefixo /protocolo é definido automaticamente no app/_init_.py
durante o registro do blueprint.
"""

from flask import Blueprint

# ==========================================================
# 🟦 Criação do Blueprint principal do módulo
# ==========================================================
protocolo_bp = Blueprint(
    'protocolo_bp',
    _name_,
    template_folder='../templates',
    static_folder='../static'
)

# ==========================================================
# 🔁 Importação das rotas (mantida no final)
# ==========================================================
from app.protocolo import routes  # noqa: E402,F401
