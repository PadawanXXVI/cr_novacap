# app/processos/routes.py
"""
Rotas do módulo de Processos (Tramitação SEI) — CR-NOVACAP.
Inclui: dashboard, cadastro, alteração, consulta unificada e exportações (CSV, XLSX, PDF).
"""

import os
from datetime import datetime
from io import BytesIO
import pandas as pd

from flask import (
    render_template, request, redirect, url_for, flash, session,
    make_response, send_file, jsonify, current_app
)
from flask_login import login_required, current_user

from app.ext import db, csrf
from app.models.modelos import (
    Processo, EntradaProcesso, Demanda, TipoDemanda, RegiaoAdministrativa,
    Status, Usuario, Movimentacao, Diretoria
)
from app.processos import processos_bp

# Bibliotecas para PDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# ==========================================================
# 1️⃣ Dashboard de Processos
# ==========================================================
@processos_bp.route('/dashboard')
@login_required
def dashboard_processos():
    """Exibe estatísticas gerais dos processos"""
    total_processos = Processo.query.count()

    # Totais consolidados
    processos_atendidos = Processo.query.filter_by(status_atual='Atendido').count()
    processos_dc = Processo.query.filter_by(diretoria_destino='Diretoria das Cidades - DC').count()
    processos_do = Processo.query.filter_by(diretoria_destino='Diretoria de Obras - DO').count()
    processos_dp = Processo.query.filter_by(diretoria_destino='Diretoria de Planejamento e Projetos - DP').count()
    processos_improcedentes = Processo.query.filter(Processo.status_atual.like('%Improcedente%')).count()
    devolvidos_ra = Processo.query.filter(Processo.status_atual.like('%Devolvido à RA%')).count()
    processos_urgentes = Processo.query.filter_by(status_atual="Solicitação de urgência").count()
    processos_prazo_execucao = Processo.query.filter_by(status_atual="Solicitação de prazo de execução").count()
    processos_ouvidoria = Processo.query.filter_by(status_atual="Processo oriundo de Ouvidoria").count()

    return render_template(
        'dashboard_processos.html',
        total_processos=total_processos,
        processos_atendidos=processos_atendidos,
        processos_dc=processos_dc,
        processos_do=processos_do,
        processos_dp=processos_dp,
        processos_improcedentes=processos_improcedentes,
        devolvidos_ra=devolvidos_ra,
        processos_urgentes=processos_urgentes,
        processos_prazo_execucao=processos_prazo_execucao,
        processos_ouvidoria=processos_ouvidoria
    )


# ==========================================================
# 2️⃣ Cadastro de Processo
# ==========================================================
@processos_bp.route('/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_processo():
    """Cadastra um novo processo SEI"""
    if request.method == 'POST':
        # Limpa e normaliza o número do processo SEI
        numero = request.form.get('numero_processo', '').strip().replace(' ', '').replace('\u200b', '')

        # Busca caso já exista no banco
        existente = Processo.query.filter(
            db.func.replace(Processo.numero_processo, ' ', '') == numero
        ).first()

        if existente:
            flash(f"⚠ O processo {numero} já está cadastrado no sistema.", "warning")
            return redirect(url_for('processos_bp.consultar_processos', numero_processo=numero))

        try:
            data_criacao_ra = datetime.strptime(request.form.get('data_criacao_ra'), "%Y-%m-%d").date()
            data_entrada_novacap = datetime.strptime(request.form.get('data_entrada_novacap'), "%Y-%m-%d").date()
            data_documento = datetime.strptime(request.form.get('data_documento'), "%Y-%m-%d").date()

            novo = Processo(
                numero_processo=numero,
                status_atual=request.form.get('status_inicial'),
                observacoes=request.form.get('observacoes'),
                diretoria_destino=request.form.get('diretoria_destino')
            )
            db.session.add(novo)
            db.session.flush()

            entrada = EntradaProcesso(
                id_processo=novo.id_processo,
                data_criacao_ra=data_criacao_ra,
                data_entrada_novacap=data_entrada_novacap,
                data_documento=data_documento,
                tramite_inicial=request.form.get('tramite_inicial'),
                ra_origem=request.form.get('ra_origem'),
                id_tipo=int(request.form.get('id_tipo')),
                id_demanda=int(request.form.get('id_demanda')),
                usuario_responsavel=int(request.form.get('usuario_responsavel')),
                status_inicial=request.form.get('status_inicial')
            )
            db.session.add(entrada)
            db.session.flush()

            primeira_mov = Movimentacao(
                id_entrada=entrada.id_entrada,
                id_usuario=entrada.usuario_responsavel,
                novo_status=entrada.status_inicial,
                observacao="Cadastro inicial do processo.",
                data=data_documento
            )
            db.session.add(primeira_mov)
            db.session.commit()

            flash(f"✅ Processo {numero} cadastrado com sucesso!", "success")
            return redirect(url_for('processos_bp.cadastro_processo'))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erro ao cadastrar processo: {str(e)}", "error")
            return redirect(url_for('processos_bp.cadastro_processo'))

    # Carrega listas para o formulário
    regioes = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra.asc()).all()
    tipos = TipoDemanda.query.order_by(TipoDemanda.descricao.asc()).all()
    demandas = Demanda.query.order_by(Demanda.descricao.asc()).all()
    status = Status.query.order_by(Status.descricao.asc()).all()
    usuarios = Usuario.query.filter_by(aprovado=True, bloqueado=False).order_by(Usuario.usuario.asc()).all()
    diretorias = Diretoria.query.order_by(Diretoria.nome_completo.asc()).all()

    return render_template(
        'cadastro_processo.html',
        regioes=regioes,
        tipos=tipos,
        demandas=demandas,
        status=status,
        usuarios=usuarios,
        diretorias=[d.nome_completo for d in diretorias]
    )

# ==========================================================
# 3️⃣ Alterar Processo
# ==========================================================
@processos_bp.route('/alterar/<int:id_processo>', methods=['GET', 'POST'])
@login_required
def alterar_processo(id_processo):
    """Atualiza o status e registra movimentação"""
    processo = Processo.query.get_or_404(id_processo)
    entrada = EntradaProcesso.query.filter_by(id_processo=id_processo).first()

    if request.method == 'POST':
        try:
            novo_status = request.form.get('novo_status')
            observacao = request.form.get('observacao')
            data_movimentacao = datetime.strptime(request.form.get('data_movimentacao'), "%Y-%m-%d")
            responsavel_id = int(request.form.get('responsavel_tecnico'))

            nova_mov = Movimentacao(
                id_entrada=entrada.id_entrada,
                id_usuario=responsavel_id,
                novo_status=novo_status,
                observacao=observacao,
                data=data_movimentacao
            )
            db.session.add(nova_mov)
            processo.status_atual = novo_status
            db.session.commit()

            flash("✅ Movimentação registrada com sucesso!", "success")
            return redirect(url_for('processos_bp.consultar_processos', numero_processo=processo.numero_processo))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erro ao atualizar processo: {str(e)}", "error")
            return redirect(url_for('processos_bp.alterar_processo', id_processo=id_processo))

    usuarios = Usuario.query.filter_by(aprovado=True, bloqueado=False).order_by(Usuario.usuario.asc()).all()
    status = Status.query.order_by(Status.descricao.asc()).all()

    return render_template(
        'alterar_processo.html',
        processo=processo,
        usuarios=usuarios,
        status=status
    )


# ==========================================================
# 4️⃣ Consulta Unificada (listar + buscar)
# ==========================================================
@processos_bp.route('/consultar', methods=['GET'])
@login_required
def consultar_processos():
    """Consulta unificada de processos"""
    numero = request.args.get('numero_processo', '').strip()
    status_filtro = request.args.get('status')
    ra = request.args.get('ra')
    diretoria = request.args.get('diretoria')
    tipo = request.args.get('tipo')
    demanda = request.args.get('demanda')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    query = db.session.query(Processo).join(EntradaProcesso)

    # Filtros dinâmicos
    if numero:
        query = query.filter(Processo.numero_processo.like(f"%{numero}%"))
    if status_filtro:
        query = query.filter(Processo.status_atual == status_filtro)
    if ra:
        query = query.filter(EntradaProcesso.ra_origem == ra)
    if diretoria:
        query = query.filter(Processo.diretoria_destino == diretoria)
    if tipo:
        query = query.filter(EntradaProcesso.id_tipo == tipo)
    if demanda:
        query = query.filter(EntradaProcesso.id_demanda == demanda)
    if inicio and fim:
        inicio_dt = datetime.strptime(inicio, "%Y-%m-%d")
        fim_dt = datetime.strptime(fim, "%Y-%m-%d")
        query = query.filter(EntradaProcesso.data_entrada_novacap.between(inicio_dt, fim_dt))
    elif inicio and not fim:
        inicio_dt = datetime.strptime(inicio, "%Y-%m-%d")
        query = query.filter(EntradaProcesso.data_entrada_novacap >= inicio_dt)
    elif fim and not inicio:
        fim_dt = datetime.strptime(fim, "%Y-%m-%d")
        query = query.filter(EntradaProcesso.data_entrada_novacap <= fim_dt)

    processos = query.order_by(Processo.id_processo.desc()).all()

    if not processos:
        flash("Nenhum processo encontrado com os filtros aplicados.", "warning")

    for p in processos:
        entrada = EntradaProcesso.query.filter_by(id_processo=p.id_processo).first()
        p.entrada = entrada
        if entrada:
            entrada.tipo = TipoDemanda.query.get(entrada.id_tipo)
            entrada.demanda = Demanda.query.get(entrada.id_demanda)
            ultima_mov = Movimentacao.query.filter_by(id_entrada=entrada.id_entrada).order_by(Movimentacao.data.desc()).first()
            p.ultima_data = ultima_mov.data if ultima_mov else entrada.data_documento

    todas_ras = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra).all()
    todos_status = Status.query.order_by(Status.ordem_exibicao).all()
    tipos = TipoDemanda.query.order_by(TipoDemanda.descricao.asc()).all()
    demandas = Demanda.query.order_by(Demanda.descricao.asc()).all()
    diretorias = [d.nome_completo for d in Diretoria.query.order_by(Diretoria.nome_completo.asc()).all()]

    return render_template(
        "consultar_processos.html",
        processos=processos,
        todas_ras=todas_ras,
        todos_status=todos_status,
        tipos=tipos,
        demandas=demandas,
        diretorias=diretorias
    )


# ==========================================================
# 5️⃣ Exportar PDF individual
# ==========================================================
@processos_bp.route('/exportar-processo/<int:id_processo>')
@login_required
def exportar_processo_pdf(id_processo):
    """Gera um PDF institucional com dados completos do processo"""
    processo = Processo.query.get_or_404(id_processo)
    entrada = EntradaProcesso.query.filter_by(id_processo=id_processo).first()
    movimentacoes = Movimentacao.query.filter_by(id_entrada=entrada.id_entrada).order_by(Movimentacao.data.asc()).all() if entrada else []

    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # ✅ Logo do GDF com caminho absoluto
    logo_path = os.path.join(current_app.root_path, "static", "images", "ico-logo-gdf.svg")
    if os.path.exists(logo_path):
        try:
            elements.append(Image(logo_path, width=80, height=60))
        except Exception:
            pass

    elements.append(Paragraph("<b>Relatório Institucional de Processo</b>", styles['Title']))
    elements.append(Spacer(1, 12))

    info_table = [
        ["Número do Processo", processo.numero_processo],
        ["Status Atual", processo.status_atual or "---"],
        ["Diretoria de Destino", processo.diretoria_destino or "---"],
        ["Observações", processo.observacoes or "---"],
    ]
    table = Table(info_table, colWidths=[160, 370])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    if entrada:
        entrada_table = [
            ["RA de Origem", entrada.ra_origem or "---"],
            ["Tramitação Inicial", entrada.tramite_inicial or "---"],
            ["Data de Entrada na NOVACAP", entrada.data_entrada_novacap.strftime("%d/%m/%Y") if entrada.data_entrada_novacap else "---"],
            ["Tipo de Demanda", entrada.tipo.descricao if entrada.tipo else "---"],
            ["Demanda", entrada.demanda.descricao if entrada.demanda else "---"],
            ["Responsável Técnico", f"{entrada.usuario_responsavel}" if entrada.usuario_responsavel else "---"]
        ]
        table = Table(entrada_table, colWidths=[200, 330])
        table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.25, colors.grey)]))
        elements.append(Paragraph("<b>Informações da Entrada</b>", styles['Heading2']))
        elements.append(table)
        elements.append(Spacer(1, 12))

    # Histórico
    elements.append(Paragraph("<b>Histórico de Movimentações</b>", styles['Heading2']))
    if movimentacoes:
        mov_table = [["Data", "Status", "Responsável", "Observação"]]
        for m in movimentacoes:
            usuario = Usuario.query.get(m.id_usuario)
            mov_table.append([
                m.data.strftime("%d/%m/%Y") if m.data else "---",
                m.novo_status or "---",
                usuario.nome if usuario else "---",
                m.observacao or "---"
            ])
        table = Table(mov_table, repeatRows=1, colWidths=[80, 120, 120, 210])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#004A8F")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("Nenhuma movimentação registrada.", styles['Normal']))

    doc.build(elements)
    output.seek(0)
    nome_arquivo = f"Processo_{processo.numero_processo.replace('/', '_')}.pdf"
    return send_file(output, as_attachment=True, download_name=nome_arquivo, mimetype='application/pdf')


# ==========================================================
# 6️⃣ Verificar processo via AJAX
# ==========================================================
@csrf.exempt
@processos_bp.route("/verificar-processo", methods=["POST"])
@login_required
def verificar_processo():
    data = request.get_json()
    numero = data.get("numero_processo")
    if not numero:
        return jsonify({"erro": "Número do processo não informado."}), 400
    processo = Processo.query.filter_by(numero_processo=numero).first()
    if processo:
        return jsonify({"existe": True, "id": processo.id_processo})
    return jsonify({"existe": False})

# ==========================================================
# 7️⃣ Exportar lista de Processos (CSV / XLSX / PDF)
# ==========================================================
@processos_bp.route('/exportar-tramitacoes', methods=['GET'])
@login_required
def exportar_tramitacoes():
    """Exporta a lista de processos filtrados (CSV, XLSX ou PDF)"""

    formato = request.args.get('formato', 'csv')
    status = request.args.get('status')
    ra = request.args.get('ra')
    diretoria = request.args.get('diretoria')
    tipo = request.args.get('tipo')
    demanda = request.args.get('demanda')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    query = Processo.query.join(EntradaProcesso, isouter=True)

    # Aplicação dos filtros (iguais à consulta principal)
    if status:
        query = query.filter(Processo.status_atual == status)
    if ra:
        query = query.filter(EntradaProcesso.ra_origem == ra)
    if diretoria:
        query = query.filter(Processo.diretoria_destino == diretoria)
    if tipo:
        query = query.filter(EntradaProcesso.id_tipo == tipo)
    if demanda:
        query = query.filter(EntradaProcesso.id_demanda == demanda)
    if inicio and fim:
        try:
            inicio_dt = datetime.strptime(inicio, "%Y-%m-%d")
            fim_dt = datetime.strptime(fim, "%Y-%m-%d")
            query = query.filter(EntradaProcesso.data_entrada_novacap.between(inicio_dt, fim_dt))
        except Exception:
            pass

    processos = query.order_by(Processo.id_processo.desc()).all()
    if not processos:
        flash("Nenhum processo encontrado para exportação.", "warning")
        return redirect(url_for('processos_bp.consultar_processos'))

    # Montagem dos dados para exportação
    dados = []
    for p in processos:
        entrada = EntradaProcesso.query.filter_by(id_processo=p.id_processo).first()
        dados.append({
            "Número do Processo": p.numero_processo,
            "Status Atual": p.status_atual or "---",
            "RA de Origem": entrada.ra_origem if entrada else "---",
            "Tipo de Demanda": TipoDemanda.query.get(entrada.id_tipo).descricao if entrada else "---",
            "Demanda": Demanda.query.get(entrada.id_demanda).descricao if entrada else "---",
            "Diretoria": p.diretoria_destino or "---",
            "Última Movimentação": (
                Movimentacao.query.filter_by(id_entrada=entrada.id_entrada)
                .order_by(Movimentacao.data.desc())
                .first()
                .data.strftime("%d/%m/%Y")
                if entrada and Movimentacao.query.filter_by(id_entrada=entrada.id_entrada).first()
                else "---"
            )
        })

    df = pd.DataFrame(dados)

    # === CSV ===
    if formato == 'csv':
        output = BytesIO()
        df.to_csv(output, index=False, sep=';', encoding='utf-8-sig')
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name='tramitacoes.csv',
            mimetype='text/csv'
        )

    # === XLSX ===
    elif formato == 'xlsx':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Tramitacoes')
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name='tramitacoes.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    # === PDF ===
    elif formato == 'pdf':
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("<b>Relatório de Processos Filtrados</b>", styles["Title"]))
        elements.append(Spacer(1, 12))

        table_data = [list(df.columns)] + df.values.tolist()
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0060a8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ('FONTSIZE', (0, 0), (-1, -1), 8)
        ]))

        elements.append(table)
        doc.build(elements)
        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name='tramitacoes.pdf',
            mimetype='application/pdf'
        )

    # === Erro ===
    flash("Formato inválido. Utilize CSV, XLSX ou PDF.", "danger")
    return redirect(url_for('processos_bp.consultar_processos'))
