import os
from dotenv import load_dotenv
from sqlalchemy import text
from app import create_app
from app.ext import db

# 🔐 Carregar variáveis de ambiente
load_dotenv()

# ⚙️ Criar app e contexto
app = create_app()
with app.app_context():
    comando_view = """
    CREATE OR REPLACE VIEW vw_processos_completos AS
    SELECT
        p.id_processo,
        p.numero_processo,
        p.status_atual AS status_final,
        p.observacoes AS obs_processo,
        p.diretoria_destino,

        ep.data_criacao_ra,
        ep.data_entrada_novacap,
        ep.ra_origem,
        ep.id_demanda,
        ep.id_tipo,
        ep.usuario_responsavel,
        ep.status_inicial,

        m.novo_status AS status_ultimo_mov,
        m.data AS data_ultima_movimentacao,
        m.observacao AS obs_movimentacao

    FROM processos p
    LEFT JOIN entradas_processo ep ON ep.id_processo = p.id_processo
    LEFT JOIN (
        SELECT m1.*
        FROM movimentacoes m1
        INNER JOIN (
            SELECT id_entrada, MAX(data) AS max_data
            FROM movimentacoes
            GROUP BY id_entrada
        ) m2
        ON m1.id_entrada = m2.id_entrada AND m1.data = m2.max_data
    ) m ON m.id_entrada = ep.id_entrada;
    """
    db.session.execute(text(comando_view))
    db.session.commit()
    print("✅ VIEW vw_processos_completos criada com sucesso!")
