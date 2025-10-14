# app/relatorios/routes.py
"""
Rotas do módulo de Relatórios — CR-NOVACAP.
Inclui relatórios gerenciais simples, avançados e exportações (CSV/XLSX/SEI).
"""

from datetime import datetime
from io import BytesIO
import pandas as pd

from flask import (
    render_template, request, redirect, url_for, flash, session,
    send_file, make_response, abort
)
from flask_login import login_required

from app.ext import db
from app.models.modelos import (
    Movimentacao, Usuario, EntradaProcesso, Processo, Demanda, Status, RegiaoAdministrativa
)
from app.relatorios import relatorios_bp


# ==========================================================
# 1️⃣ Relatórios Gerenciais Simples
# ==========================================================
@relatorios_bp.route('/gerenciais')
@login_required
def relatorios_gerenciais():
    """Relatório simples com totais de processos e tramitações"""
    total_processos = Processo.query.count()
    total_tramitacoes = Movimentacao.query.count()
    return render_template(
        'relatorios_gerenciais.html',
        total_processos=total_processos,
        total_tramitacoes=total_tramitacoes
    )


# ==========================================================
# 2️⃣ Relatórios Avançados — Tela e Filtros
# ==========================================================
@relatorios_bp.route('/avancados')
@login_required
def relatorios_avancados():
    """Tela de filtros e exibição de relatórios avançados"""
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

    status_sel = request.args.getlist('status')
    ras_sel = request.args.getlist('ra')
    diretorias_sel = request.args.getlist('diretoria')
    demandas_sel = request.args.getlist('servico')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')
    modo_status = request.args.get('modo_status', 'historico')

    query = (
        db.session.query(Movimentacao, Usuario, EntradaProcesso, Processo, Demanda)
        .join(Usuario, Movimentacao.id_usuario == Usuario.id_usuario)
        .join(EntradaProcesso, Movimentacao.id_entrada == EntradaProcesso.id_entrada)
        .join(Processo, EntradaProcesso.id_processo == Processo.id_processo)
        .join(Demanda, EntradaProcesso.id_demanda == Demanda.id_demanda)
    )

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
        except ValueError:
            flash("Formato de data inválido. Use o formato AAAA-MM-DD.", "error")

    resultados = query.order_by(Movimentacao.data.desc()).all()

    dados = [{
        "Data": mov.data.strftime("%d/%m/%Y %H:%M"),
        "Número do Processo": processo.numero_processo,
        "RA": entrada.ra_origem,
        "Status": mov.novo_status,
        "Diretoria": processo.diretoria_destino,
        "Serviço": demanda.descricao if demanda else "",
        "Responsável": user.usuario,
        "Observação": mov.observacao or ""
    } for mov, user, entrada, processo, demanda in resultados]

    df = pd.DataFrame(dados)

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
        todos_status=todos_status, todas_ras=todas_ras,
        todas_demandas=todas_demandas, diretorias=diretorias,
        resultados=resultados,
        total_resultados=len(resultados),
        modo_status=modo_status
    )


# ==========================================================
# 3️⃣ Exportação de Relatórios (CSV / XLSX)
# ==========================================================
@relatorios_bp.route('/exportar')
@login_required
def exportar_relatorios():
    """Exporta dados filtrados em CSV ou XLSX"""
    formato = request.args.get('formato', 'csv').lower()
    dados = session.get('dados_relatorio', [])

    if not dados:
        flash("Nenhum dado disponível para exportação.", "warning")
        return redirect(url_for('relatorios_bp.relatorios_avancados'))

    df = pd.DataFrame(dados)
    nome_arquivo = f"Relatorio_Avancado_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if formato == "xlsx":
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Relatório')
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name=f"{nome_arquivo}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig')
        response = make_response(csv)
        response.headers["Content-Disposition"] = f"attachment; filename={nome_arquivo}.csv"
        response.headers["Content-Type"] = "text/csv"
        return response


# ==========================================================
# 4️⃣ Geração de Relatório SEI (.docx)
# ==========================================================
@relatorios_bp.route('/gerar-sei')
@login_required
def gerar_relatorio_sei():
    """Gera relatório SEI-GDF com base nos dados do relatório avançado"""
    from gerar_relatorio_sei import gerar_relatorio_sei  # import local

    dados = session.get('dados_relatorio', [])
    filtros = session.get('filtros_ativos', {})

    if not dados:
        flash("Nenhum dado disponível para gerar relatório SEI.", "warning")
        return redirect(url_for('relatorios_bp.relatorios_avancados'))

    df = pd.DataFrame(dados)
    autor = session.get('usuario', 'Usuário desconhecido')

    try:
        caminho_arquivo = gerar_relatorio_sei(df, filtros=filtros, autor=autor)
    except Exception as e:
        print(f"Erro ao gerar relatório SEI: {e}")
        abort(500, description="Erro interno ao gerar relatório SEI.")

    return send_file(
        caminho_arquivo,
        as_attachment=True,
        download_name=f"Relatorio_SEI_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
