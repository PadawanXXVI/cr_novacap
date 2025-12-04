# app/relatorios/routes.py
"""
Módulo de Relatórios — CR-NOVACAP
---------------------------------
Este módulo contém:
 - Relatórios avançados (com filtros combinados)
 - Exportações CSV/XLSX
 - Suporte ao Painel BI
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
# 🔎 1 — RELATÓRIO AVANÇADO
# ==========================================================
@relatorios_bp.route('/avancados')
@login_required
def relatorios_avancados():
    """Tela principal de Relatórios Avançados com filtros, totais e resultados."""

    # Listas exibidas nos filtros
    todos_status = Status.query.order_by(Status.ordem_exibicao).all()
    todas_ras = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra).all()
    todas_demandas = Demanda.query.order_by(Demanda.descricao.asc()).all()

    # Diretoria exibida = descricao_exibicao da tabela
    diretorias_db = Diretoria.query.all()
    diretorias_exibicao = [d.descricao_exibicao for d in diretorias_db]

    # Filtros recebidos do HTML
    status_sel = request.args.get('status')
    ra_sel = request.args.get('ra')
    diretorias_sel = request.args.get('diretoria')
    demanda_sel = request.args.get('servico')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    # Query base
    query = (
        db.session.query(Movimentacao, Usuario, EntradaProcesso, Processo, Demanda)
        .join(Usuario, Movimentacao.id_usuario == Usuario.id_usuario)
        .join(EntradaProcesso, Movimentacao.id_entrada == EntradaProcesso.id_entrada)
        .join(Processo, EntradaProcesso.id_processo == Processo.id_processo)
        .join(Demanda, EntradaProcesso.id_demanda == Demanda.id_demanda)
    )

    # ==========================================================
    # FILTROS
    # ==========================================================

    # --- Status ---
    if status_sel and status_sel != "":
        query = query.filter(Movimentacao.novo_status == status_sel)

    # --- Região Administrativa ---
    if ra_sel and ra_sel != "":
        query = query.filter(EntradaProcesso.ra_origem == ra_sel)

    # --- Diretoria de Destino ---
    if diretorias_sel and diretorias_sel != "":
        # encontra a diretoria certa no banco
        diretoria_db = Diretoria.query.filter_by(descricao_exibicao=diretorias_sel).first()
        if diretoria_db:
            nome_salvo = diretoria_db.nome_completo  # ex.: "Diretoria das Cidades"
            query = query.filter(Processo.diretoria_destino == nome_salvo)

    # --- Demanda / Serviço ---
    if demanda_sel and demanda_sel != "":
        query = query.filter(Demanda.descricao == demanda_sel)

    # --- Datas ---
    if inicio and fim:
        try:
            dt_inicio = datetime.strptime(inicio, "%Y-%m-%d")
            dt_fim = datetime.strptime(fim, "%Y-%m-%d")
            query = query.filter(Movimentacao.data.between(dt_inicio, dt_fim))
        except ValueError:
            flash("Formato de data inválido. Use AAAA-MM-DD.", "danger")

    # ==========================================================
    # EXECUTA CONSULTA
    # ==========================================================
    resultados = query.order_by(Movimentacao.data.desc()).all()

    # ==========================================================
    # MONTA DATAFRAME PARA EXPORTAÇÃO E GRÁFICOS
    # ==========================================================
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
            "Observação": mov.observacao or ""
        })

        ras_distintas.add(entrada.ra_origem)
        if demanda:
            demandas_distintas.add(demanda.descricao)

    df = pd.DataFrame(dados)

    # Salva sessão para exportação
    session['dados_relatorio'] = df.to_dict(orient='records')

    # Totais dos cards
    total_resultados = len(resultados)
    total_ras = len(ras_distintas)
    total_demandas = len(demandas_distintas)

    # Renderiza HTML
    return render_template(
        'relatorios_avancados.html',
        todos_status=todos_status,
        todas_ras=todas_ras,
        todas_demandas=todas_demandas,
        diretorias=diretorias_exibicao,
        resultados=resultados,
        total_resultados=total_resultados,
        total_ras=total_ras,
        total_demandas=total_demandas
    )


# ==========================================================
# 📄 2 — EXPORTAÇÃO CSV / XLSX
# ==========================================================
@relatorios_bp.route('/exportar')
@login_required
def exportar_relatorios():
    """Exporta CSV ou XLSX com base nos dados filtrados."""
    
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
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # CSV
    csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig')
    response = make_response(csv)
    response.headers["Content-Disposition"] = f"attachment; filename={nome}.csv"
    response.headers["Content-Type"] = "text/csv"
    return response
