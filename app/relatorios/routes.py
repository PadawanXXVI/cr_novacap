# app/relatorios/routes.py
"""
Módulo de Relatórios — CR-NOVACAP
---------------------------------
 - Relatórios avançados (com filtros combinados)
 - Exportações CSV/XLSX
"""

from datetime import datetime
from io import BytesIO
import pandas as pd

from flask import (
    render_template, request, redirect, url_for, flash, session,
    send_file, make_response
)
from flask_login import login_required

from app.ext import db
from app.models.modelos import (
    Movimentacao, Usuario, EntradaProcesso, Processo,
    Demanda, Status, RegiaoAdministrativa, Diretoria
)

from app.relatorios import relatorios_bp


# ==========================================================
# 1️⃣ RELATÓRIO AVANÇADO — FILTROS E RESULTADOS
# ==========================================================
@relatorios_bp.route('/avancados')
@login_required
def relatorios_avancados():
    """Tela principal de Relatórios Avançados com filtros e resultados."""

    # 🔹 Listas para filtros
    todos_status = Status.query.order_by(Status.ordem_exibicao).all()
    todas_ras = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra).all()
    todas_demandas = Demanda.query.order_by(Demanda.descricao.asc()).all()

    # 🔹 Diretoria — obtida do banco
    diretorias_db = Diretoria.query.all()
    diretorias_exibicao = [d.descricao_exibicao for d in diretorias_db if d.descricao_exibicao]

    # 🔹 Mapeamento exibido → armazenado
    mapa_diretorias = {
        d.descricao_exibicao: d.nome_completo
        for d in diretorias_db if d.descricao_exibicao
    }

    # ================================
    # 🔎 Filtros recebidos (GET)
    # ================================
    status_sel = request.args.getlist('status')
    ras_sel = request.args.getlist('ra')
    diretorias_sel = request.args.getlist('diretoria')
    demandas_sel = request.args.getlist('servico')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')
    modo_status = request.args.get('modo_status', 'historico')  # histórico ou atual

    # ================================
    # 🧠 Query base
    # ================================
    query = (
        db.session.query(Movimentacao, Usuario, EntradaProcesso, Processo, Demanda)
        .join(Usuario, Movimentacao.id_usuario == Usuario.id_usuario)
        .join(EntradaProcesso, Movimentacao.id_entrada == EntradaProcesso.id_entrada)
        .join(Processo, EntradaProcesso.id_processo == Processo.id_processo)
        .join(Demanda, EntradaProcesso.id_demanda == Demanda.id_demanda)
    )

    # ================================
    # 🎯 APLICAÇÃO DOS FILTROS
    # ================================

    # ✔ Status
    if status_sel and "Todos" not in status_sel:
        if modo_status == 'atual':
            query = query.filter(Processo.status_atual.in_(status_sel))
        else:
            query = query.filter(Movimentacao.novo_status.in_(status_sel))

    # ✔ Região Administrativa
    if ras_sel and "Todas" not in ras_sel:
        query = query.filter(EntradaProcesso.ra_origem.in_(ras_sel))

    # ✔ Diretoria — corrigido com mapeamento
    if diretorias_sel and "Todas" not in diretorias_sel:
        diretorias_normalizadas = [
            mapa_diretorias.get(item)
            for item in diretorias_sel
            if mapa_diretorias.get(item)
        ]
        if diretorias_normalizadas:
            query = query.filter(Processo.diretoria_destino.in_(diretorias_normalizadas))

    # ✔ Demanda
    if demandas_sel and "Todas" not in demandas_sel:
        query = query.filter(Demanda.descricao.in_(demandas_sel))

    # ✔ Intervalo de datas
    if inicio and fim:
        try:
            inicio_dt = datetime.strptime(inicio, "%Y-%m-%d")
            fim_dt = datetime.strptime(fim, "%Y-%m-%d")
            query = query.filter(Movimentacao.data.between(inicio_dt, fim_dt))
        except ValueError:
            flash("Formato de data inválido. Use AAAA-MM-DD.", "danger")

    # ================================
    # ▶ Executa a consulta
    # ================================
    resultados = query.order_by(Movimentacao.data.desc()).all()

    # ================================
    # 📊 Prepara dataframe / cards
    # ================================
    dados = []
    ras_distintas = set()
    demandas_distintas = set()

    for mov, user, entrada, processo, demanda in resultados:
        dados.append({
            "Data": mov.data.strftime("%d/%m/%Y %H:%M"),
            "Número do Processo": processo.numero_processo,
            "RA": entrada.ra_origem,
            "Status": mov.novo_status,
            "Diretoria": processo.diretoria_destino,
            "Serviço": demanda.descricao if demanda else "",
            "Responsável": user.usuario,
            "Observação": mov.observacao or "",
        })

        ras_distintas.add(entrada.ra_origem)
        if demanda:
            demandas_distintas.add(demanda.descricao)

    df = pd.DataFrame(dados)

    # Armazena para exportação
    session['dados_relatorio'] = df.to_dict(orient='records')

    # Totais dos cards
    total_resultados = len(resultados)
    total_ras = len(ras_distintas)
    total_demandas = len(demandas_distintas)

    return render_template(
        'relatorios_avancados.html',
        todos_status=todos_status,
        todas_ras=todas_ras,
        todas_demandas=todas_demandas,
        diretorias=diretorias_exibicao,
        resultados=resultados,
        total_resultados=total_resultados,
        total_ras=total_ras,
        total_demandas=total_demandas,
        modo_status=modo_status
    )


# ==========================================================
# 2️⃣ EXPORTAÇÃO CSV / XLSX
# ==========================================================
@relatorios_bp.route('/exportar')
@login_required
def exportar_relatorios():
    """Exporta relatório avançado filtrado em CSV ou XLSX."""

    dados = session.get('dados_relatorio', [])
    if not dados:
        flash("Nenhum dado disponível para exportação.", "warning")
        return redirect(url_for('relatorios_bp.relatorios_avancados'))

    df = pd.DataFrame(dados)
    formato = request.args.get('formato', 'csv').lower()
    nome = f"Relatorio_Avancado_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # XLSX
    if formato == "xlsx":
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Relatório')
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name=f"{nome}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # CSV
    csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig')
    response = make_response(csv)
    response.headers["Content-Disposition"] = f"attachment; filename={nome}.csv"
    response.headers["Content-Type"] = "text/csv"
    return response
