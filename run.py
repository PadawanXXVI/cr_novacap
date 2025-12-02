# -- coding: utf-8 --
"""
Sistema CR-NOVACAP — Controle de Processos e Atendimentos
Versão modularizada (Flask + MySQL)
"""

from app import create_app

# ==================================================
# 🚀 Inicialização da aplicação
# ==================================================
app = create_app()

# ==================================================
# ⚙ Execução do servidor (modo desenvolvimento)
# ==================================================
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
