# app/processos/routes.py
"""
Rotas do módulo de Processos (Tramitação SEI) — CR-NOVACAP.
Inclui: dashboard, cadastro, listagem, busca, alteração e relatórios da DC.
"""

from datetime import datetime
from io import BytesIO
import pandas as pd

from flask import (
    render_template, request, redirect, url_for, flash, session, make_response, send_file
)
from flask_login import login_required, current_user

from app.ext import db
from app.models.modelos import (
    Processo, EntradaProcesso, Demanda, TipoDemanda, RegiaoAdministrativa,
    Status, Usuario, Movimentacao
)
from app.processos import processos_bp


# ==========================================================
# 1️⃣ Dashboard de Processos
# ==========================================================
@processos_bp.route('/dashboard')
@login_required
def dashboard_processos():
    """Exibe estatísticas gerais dos processos"""
    total_processos = Processo.query.count()
    processos_atendidos = Processo.query.filter_by(status_atual='Atendido').count()
    processos_dc = Processo.query.filter_by(status_atual='Enviado à Diretoria das Cidades').count()
    processos_do = Processo.query.filter_by(status_atual='Enviado à Diretoria de Obras').count()
    processos_sgia = Processo.query.filter_by(status_atual='Improcedente – tramitação via SGIA').count()
    processos_improcedentes = Processo.query.filter_by(status_atual='Improcedente – tramita por órgão diferente da NOVACAP').count()

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

            flash("✅ Processo cadastrado com sucesso!", "success")
            return redirect(url_for('processos_bp.cadastro_processo'))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erro ao cadastrar processo: {str(e)}", "error")
            return redirect(url_for('processos_bp.cadastro_processo'))

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
        regioes=regioes, tipos=tipos, demandas=demandas,
        status=status, usuarios=usuarios, diretorias=diretorias
    )


# ==========================================================
# 4️⃣ Listar Processos
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

    return render_template(
        "listar_processos.html",
        processos=processos,
        todos_status=todos_status,
        todas_ras=todas_ras
    )


# ==========================================================
# 5️⃣ Alterar Processo (nova movimentação)
# ==========================================================
@processos_bp.route('/alterar/<int:id_processo>', methods=['GET', 'POST'])
@login_required
def alterar_processo(id_processo):
    """Adiciona nova movimentação e atualiza status"""
    processo = Processo.query.get_or_404(id_processo)

    if request.method == 'POST':
        novo_status = request.form.get('novo_status')
        observacao = request.form.get('observacao')
        data_mov = request.form.get('data_movimentacao')
        id_usuario = int(request.form.get('responsavel_tecnico'))

        if not (novo_status and observacao and data_mov and id_usuario):
            flash("Todos os campos são obrigatórios.", "error")
            return redirect(url_for('processos_bp.alterar_processo', id_processo=id_processo))

        entrada = EntradaProcesso.query.filter_by(id_processo=processo.id_processo).first()
        if not entrada:
            flash("Entrada do processo não encontrada.", "error")
            return redirect(url_for('processos_bp.alterar_processo', id_processo=id_processo))

        try:
            data = datetime.strptime(data_mov, "%Y-%m-%d")
        except ValueError:
            flash("Data inválida (use AAAA-MM-DD).", "error")
            return redirect(url_for('processos_bp.alterar_processo', id_processo=id_processo))

        mov = Movimentacao(
            id_entrada=entrada.id_entrada,
            id_usuario=id_usuario,
            novo_status=novo_status,
            observacao=observacao,
            data=data
        )
        db.session.add(mov)
        processo.status_atual = novo_status
        db.session.commit()

        flash("✅ Processo atualizado com sucesso!", "success")
        return redirect(url_for('processos_bp.dashboard_processos'))

    status = Status.query.order_by(Status.ordem_exibicao).all()
    usuarios = Usuario.query.order_by(Usuario.usuario).all()

    return render_template("alterar_processo.html", processo=processo, status=status, usuarios=usuarios)


# ==========================================================
# 6️⃣ Relatório da Diretoria das Cidades (DC)
# ==========================================================
@processos_bp.route('/relatorios-dc')
@login_required
def relatorios_dc():
    """Relatório filtrado das demandas da Diretoria das Cidades"""
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    query = (
        db.session.query(Movimentacao, Usuario, EntradaProcesso, Processo, Demanda)
        .join(Usuario, Movimentacao.id_usuario == Usuario.id_usuario)
        .join(EntradaProcesso, Movimentacao.id_entrada == EntradaProcesso.id_entrada)
        .join(Processo, EntradaProcesso.id_processo == Processo.id_processo)
        .join(Demanda, EntradaProcesso.id_demanda == Demanda.id_demanda)
    )

    if inicio and fim:
        try:
            inicio_dt = datetime.strptime(inicio, "%Y-%m-%d")
            fim_dt = datetime.strptime(fim, "%Y-%m-%d")
            query = query.filter(Movimentacao.data.between(inicio_dt, fim_dt))
        except ValueError:
            flash("Formato de data inválido (AAAA-MM-DD).", "error")

    DEMANDAS_DC = [
        "Alambrado (Cercamento)", "Doação de Mudas", "Jardim", "Mato Alto",
        "Meio-fio", "Parque Infantil", "Pista de Skate", "Poda / Supressão de Árvore",
        "Ponto de Encontro Comunitário (PEC)", "Praça", "Quadra de Esporte", "Tapa-buraco"
    ]

    cond_dc = db.or_(
        Processo.diretoria_destino.ilike('%Cidades%'),
        Demanda.descricao.in_(DEMANDAS_DC)
    )
    resultados = query.filter(cond_dc).order_by(Movimentacao.data.desc()).all()

    df = pd.DataFrame([{
        "Data": mov.data.strftime("%d/%m/%Y %H:%M"),
        "Número do Processo": processo.numero_processo,
        "RA": entrada.ra_origem,
        "Status": mov.novo_status,
        "Diretoria": processo.diretoria_destino,
        "Serviço": demanda.descricao if demanda else "",
        "Responsável": user.usuario,
        "Observação": mov.observacao or ""
    } for mov, user, entrada, processo, demanda in resultados])

    total_geral = len(df)
    totais_por_servico = df['Serviço'].value_counts().to_dict() if not df.empty else {}

    session['dados_relatorio_dc'] = df.to_dict(orient='records')

    return render_template(
        'relatorios_dc.html',
        resultados=resultados,
        total_geral=total_geral,
        totais_por_servico=totais_por_servico,
        inicio=inicio,
        fim=fim
    )


# ==========================================================
# 7️⃣ Exportar Relatório DC
# ==========================================================
@processos_bp.route('/exportar-dc')
@login_required
def exportar_dc():
    """Exporta relatório da DC em CSV ou XLSX"""
    formato = request.args.get('formato', 'xlsx').lower()
    dados = session.get('dados_relatorio_dc', [])
    df = pd.DataFrame(dados)

    output = BytesIO()
    if formato == 'xlsx':
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Base_DC')
            if not df.empty:
                totais = df.groupby('Serviço').size().reset_index(name='Total')
            else:
                totais = pd.DataFrame(columns=['Serviço', 'Total'])
            totais.to_excel(writer, index=False, sheet_name='Totais_por_Servico')
            resumo = pd.DataFrame([{'Total_Geral': len(df)}])
            resumo.to_excel(writer, index=False, sheet_name='Resumo')

        output.seek(0)
        return send_file(
            output,
            as_attachment=True,
            download_name=f"Relatorio_DC_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig')
        response = make_response(csv)
        response.headers["Content-Disposition"] = "attachment; filename=relatorio_dc.csv"
        response.headers["Content-Type"] = "text/csv"
        return response
