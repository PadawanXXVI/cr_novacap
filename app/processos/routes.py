# app/processos/routes.py
"""
Rotas do módulo de Processos (Tramitação SEI) — CR-NOVACAP.
Inclui: dashboard, cadastro, listagem, busca, alteração, relatórios e exportações (CSV, XLSX, PDF).
"""

from datetime import datetime
from io import BytesIO
import pandas as pd

from flask import (
    render_template, request, redirect, url_for, flash, session,
    make_response, send_file, jsonify
)
from flask_login import login_required, current_user

from app.ext import db, csrf
from app.models.modelos import (
    Processo, EntradaProcesso, Demanda, TipoDemanda, RegiaoAdministrativa,
    Status, Usuario, Movimentacao
)
from app.processos import processos_bp

# Bibliotecas para PDF
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
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

    # Totais consolidados por status (última movimentação)
    processos_atendidos = Processo.query.filter_by(status_atual='Atendido').count()
    processos_dc = Processo.query.filter_by(diretoria_destino='Diretoria das Cidades - DC').count()
    processos_do = Processo.query.filter_by(diretoria_destino='Diretoria de Obras - DO').count()
    processos_dp = Processo.query.filter_by(diretoria_destino='Diretoria de Planejamento e Projetos - DP').count()
    processos_sgia = Processo.query.filter_by(status_atual='Improcedente – tramitação via SGIA').count()
    processos_improcedentes = Processo.query.filter_by(
        status_atual='Improcedente – tramita por órgão diferente da NOVACAP'
    ).count()

    devolvidos_ra = Processo.query.filter(
        Processo.status_atual.in_([
            "Devolvido à RA de origem – adequação de requisitos",
            "Devolvido à RA de origem – parecer técnico de outro órgão",
            "Devolvido à RA de origem – serviço com contrato de natureza continuada pela DC/DO",
            "Devolvido à RA de origem – implantação"
        ])
    ).count()

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
        processos_sgia=processos_sgia,
        processos_improcedentes=processos_improcedentes,
        devolvidos_ra=devolvidos_ra,
        processos_urgentes=processos_urgentes,
        processos_prazo_execucao=processos_prazo_execucao,
        processos_ouvidoria=processos_ouvidoria
    )


# ==========================================================
# 2️⃣ Buscar Processo
# ==========================================================
@processos_bp.route('/buscar', methods=['GET'])
@login_required
def buscar_processo():
    """Busca um processo pelo número"""
    numero = request.args.get('numero_processo')
    processo = Processo.query.filter_by(numero_processo=numero).first()

    if not processo:
        flash("❌ Processo não localizado.", "error")
        return render_template('visualizar_processo.html', processo=None)

    entrada = EntradaProcesso.query.filter_by(id_processo=processo.id_processo).first()
    movimentacoes = []

    if entrada:
        entrada.tipo = TipoDemanda.query.get(entrada.id_tipo)
        entrada.responsavel = Usuario.query.get(entrada.usuario_responsavel)
        movimentacoes = (
            db.session.query(Movimentacao)
            .filter(Movimentacao.id_entrada == entrada.id_entrada)
            .order_by(Movimentacao.data.asc())
            .all()
        )

    ultima_obs = movimentacoes[-1].observacao if movimentacoes else processo.observacoes

    return render_template(
        'visualizar_processo.html',
        processo=processo,
        entrada=entrada,
        movimentacoes=movimentacoes,
        ultima_observacao=ultima_obs
    )


# ==========================================================
# 3️⃣ Cadastro de Processo
# ==========================================================
@processos_bp.route('/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_processo():
    """Cadastra um novo processo SEI"""
    if request.method == 'POST':
        numero = request.form.get('numero_processo', '').strip()
        existente = Processo.query.filter_by(numero_processo=numero).first()

        if existente:
            flash("⚠️ Processo já cadastrado. Redirecionando...", "warning")
            return redirect(url_for('processos_bp.alterar_processo', id_processo=existente.id_processo))

        try:
            # 🗓️ Conversões de datas
            data_criacao_ra = datetime.strptime(request.form.get('data_criacao_ra'), "%Y-%m-%d").date()
            data_entrada_novacap = datetime.strptime(request.form.get('data_entrada_novacap'), "%Y-%m-%d").date()
            data_documento = datetime.strptime(request.form.get('data_documento'), "%Y-%m-%d").date()

            # 🧱 Criação do processo principal
            novo = Processo(
                numero_processo=numero,
                status_atual=request.form.get('status_inicial'),
                observacoes=request.form.get('observacoes'),
                diretoria_destino=request.form.get('diretoria_destino')
            )
            db.session.add(novo)
            db.session.flush()  # 🔥 Garante que id_processo esteja disponível

            # 🧩 Entrada inicial (registro de origem)
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

            # 🔁 Primeira movimentação do processo
            primeira_mov = Movimentacao(
                id_entrada=entrada.id_entrada,
                id_usuario=entrada.usuario_responsavel,
                novo_status=entrada.status_inicial,
                observacao="Cadastro inicial do processo.",
                data=data_documento
            )
            db.session.add(primeira_mov)

            db.session.commit()
            flash("✅ Processo cadastrado com sucesso!", "success")
            return redirect(url_for('processos_bp.cadastro_processo'))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erro ao cadastrar processo: {str(e)}", "error")
            return redirect(url_for('processos_bp.cadastro_processo'))

    # 🔽 Dados auxiliares
    regioes = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra.asc()).all()
    tipos = TipoDemanda.query.order_by(TipoDemanda.descricao.asc()).all()
    demandas = Demanda.query.order_by(Demanda.descricao.asc()).all()
    status = Status.query.order_by(Status.descricao.asc()).all()
    usuarios = Usuario.query.filter_by(aprovado=True, bloqueado=False).order_by(Usuario.usuario.asc()).all()

    diretorias = [
        "Diretoria das Cidades - DC",
        "Diretoria de Obras - DO",
        "Diretoria de Planejamento e Projetos - DP",
        "Diretoria de Suporte - DS",
        "Não tramita na Novacap",
        "Tramita via SGIA",
    ]

    return render_template(
        'cadastro_processo.html',
        regioes=regioes,
        tipos=tipos,
        demandas=demandas,
        status=status,
        usuarios=usuarios,
        diretorias=diretorias
    )


# ==========================================================
# 4️⃣ Alterar Processo (Atualizar Status / Registrar Movimentação)
# ==========================================================
@processos_bp.route('/alterar/<int:id_processo>', methods=['GET', 'POST'])
@login_required
def alterar_processo(id_processo):
    """Atualiza o status de um processo e registra nova movimentação"""
    processo = Processo.query.get_or_404(id_processo)
    entrada = EntradaProcesso.query.filter_by(id_processo=id_processo).first()

    if request.method == 'POST':
        try:
            novo_status = request.form.get('novo_status')
            observacao = request.form.get('observacao')
            data_movimentacao = datetime.strptime(request.form.get('data_movimentacao'), "%Y-%m-%d")
            responsavel_id = int(request.form.get('responsavel_tecnico'))

            # 🔁 Registra nova movimentação
            nova_mov = Movimentacao(
                id_entrada=entrada.id_entrada,
                id_usuario=responsavel_id,
                novo_status=novo_status,
                observacao=observacao,
                data=data_movimentacao
            )
            db.session.add(nova_mov)

            # 🏷️ Atualiza status atual do processo (mantém diretoria)
            processo.status_atual = novo_status
            db.session.commit()

            flash("✅ Processo atualizado e movimentação registrada com sucesso!", "success")
            return redirect(url_for('processos_bp.buscar_processo', numero_processo=processo.numero_processo))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erro ao atualizar o processo: {str(e)}", "error")
            return redirect(url_for('processos_bp.alterar_processo', id_processo=id_processo))

    # GET → renderiza formulário
    usuarios = Usuario.query.filter_by(aprovado=True, bloqueado=False).order_by(Usuario.usuario.asc()).all()
    status = Status.query.order_by(Status.descricao.asc()).all()

    return render_template(
        'alterar_processo.html',
        processo=processo,
        usuarios=usuarios,
        status=status
    )


# ==========================================================
# 5️⃣ Listar Processos + Exportações (CSV, XLSX, PDF)
# ==========================================================
@processos_bp.route('/listar')
@login_required
def listar_processos():
    """Lista os processos cadastrados com filtros"""
    status_filtro = request.args.get('status')
    ra = request.args.get('ra')
    diretoria = request.args.get('diretoria')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    query = db.session.query(Processo).join(EntradaProcesso)

    if status_filtro:
        query = query.filter(Processo.status_atual == status_filtro)
    if ra:
        query = query.filter(EntradaProcesso.ra_origem == ra)
    if diretoria:
        query = query.filter(Processo.diretoria_destino == diretoria)
    if inicio and fim:
        query = query.filter(EntradaProcesso.data_entrada_novacap.between(inicio, fim))

    processos = query.order_by(Processo.id_processo.desc()).all()

    # 🔁 Complementa com dados auxiliares
    for p in processos:
        entrada = EntradaProcesso.query.filter_by(id_processo=p.id_processo).first()
        p.entrada = entrada
        if entrada:
            entrada.tipo = TipoDemanda.query.get(entrada.id_tipo)
            entrada.movimentacoes = Movimentacao.query.filter_by(id_entrada=entrada.id_entrada).all()
            p.ultima_data = (
                entrada.movimentacoes[-1].data if entrada.movimentacoes else entrada.data_documento
            )

    todos_status = Status.query.order_by(Status.ordem_exibicao).all()
    todas_ras = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra).all()
    diretorias = [
        "Diretoria das Cidades - DC",
        "Diretoria de Obras - DO",
        "Diretoria de Planejamento e Projetos - DP",
        "Diretoria de Suporte - DS",
        "Não tramita na Novacap",
        "Tramita via SGIA",
    ]

    return render_template(
        "listar_processos.html",
        processos=processos,
        todos_status=todos_status,
        todas_ras=todas_ras,
        diretorias=diretorias
    )


# ==========================================================
# 6️⃣ Exportar Tramitações (CSV / XLSX / PDF)
# ==========================================================
@processos_bp.route('/exportar-tramitacoes', methods=['GET'])
@login_required
def exportar_tramitacoes():
    """Exporta lista de tramitações filtradas"""
    formato = request.args.get('formato', 'csv')
    status = request.args.get('status')
    ra = request.args.get('ra')
    diretoria = request.args.get('diretoria')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    query = Processo.query.join(EntradaProcesso, isouter=True)
    if status:
        query = query.filter(Processo.status_atual == status)
    if ra:
        query = query.filter(EntradaProcesso.ra_origem == ra)
    if diretoria:
        query = query.filter(Processo.diretoria_destino == diretoria)
    if inicio and fim:
        query = query.filter(EntradaProcesso.data_entrada_novacap.between(inicio, fim))

    processos = query.all()
    dados = []
    for p in processos:
        entrada = EntradaProcesso.query.filter_by(id_processo=p.id_processo).first()
        dados.append({
            "Número do Processo": p.numero_processo,
            "Status Atual": p.status_atual or "---",
            "RA de Origem": entrada.ra_origem if entrada else "---",
            "Tipo de Demanda": entrada.tipo.descricao if entrada and entrada.tipo else "---",
            "Diretoria": p.diretoria_destino or "---",
            "Última Movimentação": entrada.data_documento.strftime("%d/%m/%Y") if entrada else "---"
        })

    df = pd.DataFrame(dados)

    # CSV
    if formato == 'csv':
        output = BytesIO()
        df.to_csv(output, index=False, sep=';', encoding='utf-8-sig')
        output.seek(0)
        return send_file(output, as_attachment=True, download_name='tramitacoes.csv', mimetype='text/csv')

    # XLSX
    elif formato == 'xlsx':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Tramitacoes')
        output.seek(0)
        return send_file(output, as_attachment=True,
                         download_name='tramitacoes.xlsx',
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    # PDF
    elif formato == 'pdf':
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()
        title = Paragraph("Relatório de Tramitação de Processos", styles["Title"])
        elements.append(title)
        elements.append(Spacer(1, 12))
        table_data = [list(df.columns)] + df.values.tolist()
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0060a8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))
        elements.append(table)
        doc.build(elements)
        output.seek(0)
        return send_file(output, as_attachment=True, download_name='tramitacoes.pdf', mimetype='application/pdf')

    return make_response("Formato inválido. Use csv, xlsx ou pdf.", 400)


# ==========================================================
# 7️⃣ Verificar se o processo já existe (AJAX)
# ==========================================================
@csrf.exempt  # ✅ evita conflito com CSRF em requisições fetch()
@processos_bp.route("/verificar-processo", methods=["POST"])
@login_required
def verificar_processo():
    """Verifica via AJAX se o número de processo já existe"""
    data = request.get_json()
    numero = data.get("numero_processo")

    if not numero:
        return jsonify({"erro": "Número do processo não informado."}), 400

    processo = Processo.query.filter_by(numero_processo=numero).first()
    if processo:
        return jsonify({"existe": True, "id": processo.id_processo})
    return jsonify({"existe": False})
