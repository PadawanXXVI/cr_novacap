# app/relatorios/routes.py
"""
Módulo de Relatórios — CR-NOVACAP
---------------------------------
Este módulo contém:
 - Relatórios avançados (com filtros combinados)
 - Exportações CSV/XLSX
 - Suporte ao Painel BI

A funcionalidade de Relatório SEI (.docx) foi removida.
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
    Demanda, Status, RegiaoAdministrativa
)

from app.relatorios import relatorios_bp


# ==========================================================
# 1️⃣ RELATÓRIO AVANÇADO — FILTROS E RESULTADOS
# ==========================================================
@relatorios_bp.route('/avancados')
@login_required
def relatorios_avancados():
    """Tela principal de Relatórios Avançados com filtros e resultados."""

    # Listas para filtros
    todos_status = Status.query.order_by(Status.ordem_exibicao).all()
    todas_ras = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra).all()
    todas_demandas = Demanda.query.order_by(Demanda.descricao.asc()).all()

    diretorias = [
        "Diretoria das Cidades - DC",
        "Diretoria de Obras - DO",
        "Diretoria de Planejamento e Projetos - DP",
        "Diretoria de Suporte - DS",
        "Não tramita na Novacap",
        "Tramita via SGIA",
    ]

    # Filtros recebidos
    status_sel = request.args.getlist('status')
    ras_sel = request.args.getlist('ra')
    diretorias_sel = request.args.getlist('diretoria')
    demandas_sel = request.args.getlist('servico')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')
    modo_status = request.args.get('modo_status', 'historico')

    # Query principal
    query = (
        db.session.query(Movimentacao, Usuario, EntradaProcesso, Processo, Demanda)
        .join(Usuario, Movimentacao.id_usuario == Usuario.id_usuario)
        .join(EntradaProcesso, Movimentacao.id_entrada == EntradaProcesso.id_entrada)
        .join(Processo, EntradaProcesso.id_processo == Processo.id_processo)
        .join(Demanda, EntradaProcesso.id_demanda == Demanda.id_demanda)
    )

    # Filtros dinâmicos
    if status_sel and "Todos" not in status_sel:
        if modo_status == 'atual':
            query = query.filter(Processo.status_atual.in_(status_sel))
        else:
            query = query.filter(Movimentacao.novo_status.in_(status_sel))

    if ras_sel and "Todas" not in ras_sel:
        query = query.filter(EntradaProcesso.ra_origem.in_(ras_sel))

    if diretorias_sel and "Todas" not in diretorias_sel:
        query = query.filter(Processo.diretoria_destino.in_(diretorias_sel))

    if demandas_sel and "Todas" not in demandas_sel:
        query = query.filter(Demanda.descricao.in_(demandas_sel))

    if inicio and fim:
        try:
            inicio_dt = datetime.strptime(inicio, "%Y-%m-%d")
            fim_dt = datetime.strptime(fim, "%Y-%m-%d")
            query = query.filter(Movimentacao.data.between(inicio_dt, fim_dt))
        except:
            flash("Formato de data inválido. Use AAAA-MM-DD.", "danger")

    # Executa
    resultados = query.order_by(Movimentacao.data.desc()).all()

    # Monta DataFrame
    dados = [
        {
            "Data": mov.data.strftime("%d/%m/%Y %H:%M"),
            "Número do Processo": processo.numero_processo,
            "RA": entrada.ra_origem,
            "Status": mov.novo_status,
            "Diretoria": processo.diretoria_destino,
            "Serviço": demanda.descricao if demanda else "",
            "Responsável": user.usuario,
            "Observação": mov.observacao or ""
        }
        for mov, user, entrada, processo, demanda in resultados
    ]

    df = pd.DataFrame(dados)

    # Guarda na sessão
    session['dados_relatorio'] = df.to_dict(orient='records')
    session['filtros_ativos'] = {
        "status": status_sel,
        "ra": ras_sel,
        "diretoria": diretorias_sel,
        "servico": demandas_sel,
        "inicio": inicio,
        "fim": fim,
        "modo_status": modo_status,
    }

    return render_template(
        'relatorios_avancados.html',
        todos_status=todos_status,
        todas_ras=todas_ras,
        todas_demandas=todas_demandas,
        diretorias=diretorias,
        resultados=resultados,
        total_resultados=len(resultados),
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
