from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, send_file, jsonify, abort
from flask_login import login_required, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app
from app.ext import db
from app.models.modelos import Processo, EntradaProcesso, Demanda, TipoDemanda, RegiaoAdministrativa, Status, Usuario, Movimentacao, ProtocoloAtendimento, InteracaoAtendimento
from datetime import datetime
from io import BytesIO
import pandas as pd
import os

app = create_app()

# ================================
# ROTA 1: Tela inicial
# ================================
@app.route('/')
def index():
    return render_template('index.html')

# ================================
# ROTA 2: Login com autenticação
# ================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        senha = request.form.get('password')
        sistema = request.form.get('sistema')

        usuario = Usuario.query.filter_by(usuario=username).first()

        if not usuario:
            return "Erro: usuário não encontrado.", 404

        if not check_password_hash(usuario.senha_hash, senha):
            return "Erro: senha incorreta.", 401

        if not usuario.aprovado:
            return "Erro: acesso ainda não autorizado pelo administrador.", 403

        if usuario.bloqueado:
            return "Erro: usuário bloqueado.", 403

        login_user(usuario)
        session['usuario'] = usuario.usuario
        session['is_admin'] = usuario.is_admin
        session['id_usuario'] = usuario.id_usuario

        if sistema == 'tramite':
            return redirect(url_for('dashboard_processos'))
        elif sistema == 'protocolo':
            return redirect(url_for('dashboard_protocolo'))
        else:
            return "Sistema inválido", 400

    return render_template('login.html')

# ================================
# ROTA 3: Cadastro de Usuário
# ================================
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome_completo')
        email = request.form.get('email')
        usuario = request.form.get('username')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')

        if senha != confirmar_senha:
            flash("Erro: as senhas não coincidem.")
            return redirect(url_for('cadastro'))

        existente = Usuario.query.filter((Usuario.usuario == usuario) | (Usuario.email == email)).first()

        if existente:
            flash("Erro: e-mail ou nome de usuário já cadastrado.")
            return redirect(url_for('cadastro'))

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            usuario=usuario,
            senha_hash=generate_password_hash(senha),
            aprovado=False,
            bloqueado=False,
            is_admin=False
        )

        db.session.add(novo_usuario)
        db.session.commit()

        flash("Cadastro enviado com sucesso. Aguarde aprovação do administrador.")
        return redirect(url_for('index'))

    return render_template('cadastro.html')

# ================================
# ROTA 4: Redefinir Senha
# ================================
@app.route('/trocar-senha', methods=['GET', 'POST'])
def trocar_senha():
    if request.method == 'POST':
        nome = request.form.get('nome_completo')
        email = request.form.get('email')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')

        if nova_senha != confirmar_senha:
            flash("Erro: as senhas não coincidem.", "error")
            return redirect(url_for('trocar_senha'))

        usuario = Usuario.query.filter_by(nome=nome, email=email).first()

        if usuario:
            usuario.senha_hash = generate_password_hash(nova_senha)
            db.session.commit()
            flash("Senha atualizada com sucesso. Faça login com sua nova senha.", "success")
            return redirect(url_for('login'))
        else:
            flash("Erro: dados não encontrados. Verifique o nome e e-mail informados.", "error")
            return redirect(url_for('trocar_senha'))

    return render_template('trocar_senha.html')

# ================================
# ROTA 5: Dashboard de Processos
# ================================
@app.route('/dashboard-processos')
def dashboard_processos():
    if not session.get('usuario'):
        return redirect(url_for('login'))

    total_processos = Processo.query.count()
    processos_atendidos = Processo.query.filter_by(status_atual='Atendido').count()
    processos_dc = Processo.query.filter_by(status_atual='Enviado à Diretoria das Cidades').count()
    processos_do = Processo.query.filter_by(status_atual='Enviado à Diretoria de Obras').count()
    total_em_atendimento = processos_dc + processos_do

    return render_template(
        'dashboard_processos.html',
        total_processos=total_processos,
        processos_atendidos=processos_atendidos,
        processos_dc=processos_dc,
        processos_do=processos_do,
        total_em_atendimento=total_em_atendimento
    )

# ================================
# ROTA 6: Buscar Processo
# ================================
@app.route('/buscar-processo', methods=['GET'])
def buscar_processo():
    if not session.get('usuario'):
        return redirect(url_for('login'))

    numero = request.args.get('numero_processo')
    processo = Processo.query.filter_by(numero_processo=numero).first()

    if not processo:
        flash("❌ Processo não localizado.", "error")
        return render_template('visualizar_processo.html', processo=None)

    entrada = EntradaProcesso.query.filter_by(id_processo=processo.id_processo).first()
    movimentacoes = []

    if entrada:
        movimentacoes = db.session.query(Movimentacao).join(Usuario).filter(
            Movimentacao.id_entrada == entrada.id_entrada
        ).order_by(Movimentacao.data.asc()).all()

    return render_template(
        'visualizar_processo.html',
        processo=processo,
        entrada=entrada,
        movimentacoes=movimentacoes
    )

# ================================
# ROTA 7: Verificar Processo
# ================================
@app.route('/verificar-processo', methods=['POST'])
def verificar_processo():
    data = request.get_json()
    numero = data.get('numero_processo')
    processo = Processo.query.filter_by(numero_processo=numero).first()
    return jsonify({"existe": bool(processo)})

# ================================
# ROTA 8: Cadastro de Processo
# ================================
@app.route('/cadastro-processo', methods=['GET', 'POST'])
@login_required
def cadastro_processo():
    if request.method == 'POST':
        numero = request.form.get('numero_processo').strip()
        processo_existente = Processo.query.filter_by(numero_processo=numero).first()
        if processo_existente:
            flash("⚠️ Processo já cadastrado.", "warning")
            return redirect(url_for('alterar_processo', id_processo=processo_existente.id_processo))

        try:
            data_documento = datetime.strptime(request.form.get('data_documento'), "%Y-%m-%d").date()

            novo_processo = Processo(
                numero_processo=numero,
                status_atual=request.form.get('status_inicial'),
                observacoes=request.form.get('observacoes'),
                diretoria_destino=request.form.get('diretoria_destino')
            )
            db.session.add(novo_processo)
            db.session.flush()

            entrada = EntradaProcesso(
                id_processo=novo_processo.id_processo,
                data_documento=data_documento,
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
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erro ao cadastrar processo: {str(e)}", "error")

    regioes = RegiaoAdministrativa.query.all()
    tipos = TipoDemanda.query.all()
    demandas = Demanda.query.all()
    status = Status.query.all()
    usuarios = Usuario.query.all()
    return render_template('cadastro_processo.html', regioes=regioes, tipos=tipos, demandas=demandas, status=status, usuarios=usuarios)

# ================================
# ROTA 9: Listar Processos
# ================================
@app.route('/listar-processos')
def listar_processos():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    processos = Processo.query.order_by(Processo.id_processo.desc()).all()
    return render_template('listar_processos.html', processos=processos)

# ================================
# ROTA 10: Alterar Processo
# ================================
@app.route('/alterar-processo/<int:id_processo>', methods=['GET', 'POST'])
def alterar_processo(id_processo):
    processo = Processo.query.get_or_404(id_processo)
    if request.method == 'POST':
        novo_status = request.form.get('novo_status')
        observacao = request.form.get('observacao')
        data_movimentacao = datetime.strptime(request.form.get('data_movimentacao'), "%Y-%m-%d")
        id_usuario = int(request.form.get('responsavel_tecnico'))

        entrada = EntradaProcesso.query.filter_by(id_processo=id_processo).first()
        nova_mov = Movimentacao(
            id_entrada=entrada.id_entrada,
            id_usuario=id_usuario,
            novo_status=novo_status,
            observacao=observacao,
            data=data_movimentacao
        )
        db.session.add(nova_mov)
        processo.status_atual = novo_status
        db.session.commit()
        flash("✅ Processo alterado com sucesso!", "success")
        return redirect(url_for('dashboard_processos'))

    status = Status.query.all()
    usuarios = Usuario.query.all()
    return render_template('alterar_processo.html', processo=processo, status=status, usuarios=usuarios)

# ================================
# ROTA 11: Painel Administrativo
# ================================
@app.route('/painel-admin')
def painel_admin():
    if not session.get('is_admin'):
        return "Acesso restrito ao administrador.", 403

    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return render_template('painel-admin.html', usuarios=usuarios)

# ================================
# ROTA 12: Aprovar Usuário
# ================================
@app.route('/aprovar-usuario/<int:id_usuario>', methods=['POST'])
def aprovar_usuario(id_usuario):
    if not session.get('is_admin'):
        return "Acesso restrito ao administrador.", 403

    usuario = Usuario.query.get_or_404(id_usuario)
    usuario.aprovado = True
    db.session.commit()
    flash(f"Usuário {usuario.usuario} aprovado com sucesso.")
    return redirect(url_for('painel_admin'))

# ================================
# ROTA 13: Bloquear usuário
# ================================
@app.route('/bloquear-usuario/<int:id_usuario>', methods=['POST'])
def bloquear_usuario(id_usuario):
    if not session.get('is_admin'):
        return "Acesso restrito ao administrador.", 403

    usuario = Usuario.query.get_or_404(id_usuario)
    usuario.bloqueado = True
    db.session.commit()
    flash(f"Usuário {usuario.usuario} foi bloqueado.")
    return redirect(url_for('painel_admin'))

# ================================
# ROTA 14: Tornar usuário admin
# ================================
@app.route('/atribuir-admin/<int:id_usuario>', methods=['POST'])
def atribuir_admin(id_usuario):
    if not session.get('is_admin'):
        return "Acesso restrito ao administrador.", 403

    usuario = Usuario.query.get_or_404(id_usuario)
    usuario.is_admin = True
    db.session.commit()
    flash(f"Usuário {usuario.usuario} agora é administrador.")
    return redirect(url_for('painel_admin'))

# ================================
# ROTA 15: Logout
# ================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ================================
# ROTA 16: Relatórios Gerenciais
# ================================
@app.route('/relatorios-gerenciais')
def relatorios_gerenciais():
    if not session.get('usuario'):
        return redirect(url_for('login'))

    total_processos = Processo.query.count()
    total_tramitacoes = Movimentacao.query.count()

    return render_template(
        'relatorios_gerenciais.html',
        total_processos=total_processos,
        total_tramitacoes=total_tramitacoes
    )

# ===================================
# ROTA 17: Exportação de Tramitações (COM MODO_STATUS)
# ===================================
@app.route('/exportar-tramitacoes')
def exportar_tramitacoes():
    if not session.get('usuario'):
        return redirect(url_for('login'))

    # Parâmetros de filtro
    ra = request.args.get('ra')
    usuario = request.args.get('usuario')
    status = request.args.get('status')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')
    formato = request.args.get('formato', 'csv').lower()  # padrão: CSV
    modo_status = request.args.get('modo_status')  # novo parâmetro

    # Consulta base
    query = db.session.query(Movimentacao, Usuario, EntradaProcesso, Processo) \
        .join(Usuario, Movimentacao.id_usuario == Usuario.id_usuario) \
        .join(EntradaProcesso, Movimentacao.id_entrada == EntradaProcesso.id_entrada) \
        .join(Processo, EntradaProcesso.id_processo == Processo.id_processo)

    # Aplicar filtros
    if status:
        if modo_status == 'atual':
            query = query.filter(Processo.status_atual == status)
        else:
            query = query.filter(Movimentacao.novo_status == status)
    if ra:
        query = query.filter(EntradaProcesso.ra_origem == ra)
    if usuario:
        query = query.filter(Usuario.usuario == usuario)
    if inicio and fim:
        query = query.filter(Movimentacao.data.between(inicio, fim))

    resultados = query.order_by(Movimentacao.data.desc()).all()

    # Monta dados
    dados = []
    for mov, user, entrada, processo in resultados:
        dados.append({
            "Número do Processo": processo.numero_processo,
            "RA de Origem": entrada.ra_origem,
            "Status da Tramitação": mov.novo_status,
            "Data da Tramitação": mov.data.strftime('%d/%m/%Y %H:%M'),
            "Responsável Técnico": user.usuario,
            "Observação": mov.observacao or ''
        })

    # Exporta CSV
    if formato == 'csv':
        df = pd.DataFrame(dados)
        csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig')
        response = make_response(csv)
        response.headers["Content-Disposition"] = "attachment; filename=tramitacoes_filtradas.csv"
        response.headers["Content-Type"] = "text/csv"
        return response

    # Exporta XLSX
    elif formato == 'xlsx':
        df = pd.DataFrame(dados)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Tramitações')
        output.seek(0)

        response = send_file(output,
                             download_name="tramitacoes_filtradas.xlsx",
                             as_attachment=True,
                             mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        return response

    else:
        return "Formato inválido. Use 'csv' ou 'xlsx'.", 400

# ================================
# ROTA 18: Relatórios Avançados (MULTIFILTROS + TOTAIS POR DIRETORIA)
# ================================
@app.route('/relatorios-avancados')
def relatorios_avancados():
    if not session.get('usuario'):
        return redirect(url_for('login'))

    # ====== Listas para filtros ======
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

    # ====== Parâmetros de filtro ======
    status_sel = request.args.getlist('status')
    ras_sel = request.args.getlist('ra')
    diretorias_sel = request.args.getlist('diretoria')
    demandas_sel = request.args.getlist('servico')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')
    modo_status = request.args.get('modo_status', 'historico')

    # ====== Query base ======
    query = (
        db.session.query(Movimentacao, Usuario, EntradaProcesso, Processo, Demanda)
        .join(Usuario, Movimentacao.id_usuario == Usuario.id_usuario)
        .join(EntradaProcesso, Movimentacao.id_entrada == EntradaProcesso.id_entrada)
        .join(Processo, EntradaProcesso.id_processo == Processo.id_processo)
        .join(Demanda, EntradaProcesso.id_demanda == Demanda.id_demanda)
    )

    # ====== Aplicação dos filtros ======
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

    # ====== Prepara DataFrame para exportações e SEI ======
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

    # ====== Armazena filtros e DataFrame na sessão ======
    session['filtros_ativos'] = {
        "status": status_sel,
        "ra": ras_sel,
        "diretoria": diretorias_sel,
        "servico": demandas_sel,
        "inicio": inicio,
        "fim": fim,
        "modo_status": modo_status,
    }
    session['dados_relatorio'] = df.to_dict(orient='records')

    # ====== Renderização ======
    return render_template(
        'relatorios_avancados.html',
        todos_status=todos_status,
        todas_ras=todas_ras,
        todas_demandas=todas_demandas,
        diretorias=diretorias,
        resultados=resultados,
        modo_status=modo_status,
        total_resultados=len(resultados)
    )

# ===========================================
# ROTA 19: Exportar Relatório Avançado (CSV / Excel)
# ===========================================
@app.route('/exportar-tramitacoes')
def exportar_tramitacoes():
    if not session.get('usuario'):
        return redirect(url_for('login'))

    formato = request.args.get('formato', 'csv').lower()
    dados = session.get('dados_relatorio', [])

    if not dados:
        flash("Nenhum dado encontrado para exportação. Filtre os relatórios novamente.", "warning")
        return redirect(url_for('relatorios_avancados'))

    df = pd.DataFrame(dados)

    data_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_base = f"Relatorio_Avancado_{data_str}"
    pasta_export = os.path.join(os.path.dirname(__file__), "relatorios_gerados")
    os.makedirs(pasta_export, exist_ok=True)

    if formato == "xlsx":
        caminho = os.path.join(pasta_export, f"{nome_base}.xlsx")
        df.to_excel(caminho, index=False)
    else:
        caminho = os.path.join(pasta_export, f"{nome_base}.csv")
        df.to_csv(caminho, index=False, sep=";", encoding="utf-8-sig")

    return send_file(caminho, as_attachment=True)

# ================================
# ROTA 20: Visualizar Processo
# ================================
@app.route('/visualizar-processo')
def visualizar_processo_form():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    return render_template('visualizar_processo.html', processo=None)

# ================================
# ROTA 21: Dashboard de Protocolo
# ================================
@app.route('/dashboard-protocolo')
def dashboard_protocolo():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    return render_template('dashboard_protocolo.html')

# ================================
# ROTA 22: Cadastro de Atendimento
# ================================
@app.route('/cadastro-atendimento', methods=['GET', 'POST'])
@login_required
def cadastro_atendimento():
    if request.method == 'POST':
        try:
            atendimento = ProtocoloAtendimento(
                data_hora=datetime.now(),
                numero_protocolo=None,  # será gerado após o flush
                numero_processo_sei=request.form.get('numero_processo_sei'),
                numero_requisicao=request.form.get('numero_requisicao'),
                nome_solicitante=request.form.get('nome_solicitante'),
                tipo_solicitante=request.form.get('tipo_solicitante'),
                contato_telefone=request.form.get('contato_telefone'),
                contato_email=request.form.get('contato_email'),
                ra_origem=request.form.get('ra_origem'),
                demanda=request.form.get('demanda'),
                assunto=request.form.get('assunto'),
                encaminhamento_inicial=request.form.get('encaminhamento_inicial'),
                id_usuario_criador=session['id_usuario']
            )

            db.session.add(atendimento)
            db.session.flush()

            # Gera número de protocolo: CR-0001/2025
            ano = atendimento.data_hora.year
            numero_formatado = f"CR-{atendimento.id:04d}/{ano}"
            atendimento.numero_protocolo = numero_formatado

            db.session.commit()

            flash(f"✅ Atendimento registrado com protocolo {numero_formatado}", "success")
            return redirect(url_for('cadastro_atendimento'))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erro ao registrar atendimento: {str(e)}", "error")
            return redirect(url_for('cadastro_atendimento'))

    # Se for GET, carregar RA e demandas
    ras = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra).all()
    demandas = Demanda.query.order_by(Demanda.descricao).all()

    return render_template("cadastro_atendimento.html", ras=ras, demandas=demandas)

# ================================
# ROTA 23: Listar Atendimentos
# ================================
@app.route('/listar-atendimentos')
@login_required
def listar_atendimentos():
    atendimentos = ProtocoloAtendimento.query.order_by(ProtocoloAtendimento.data_hora.desc()).all()
    return render_template('listar_atendimentos.html', atendimentos=atendimentos)

# ================================
# ROTA 24: Buscar Atendimento por Protocolo
# ================================
@app.route('/buscar-atendimento', methods=['GET', 'POST'])
@login_required
def buscar_atendimento():
    if request.method == 'POST':
        numero_protocolo = request.form.get('numero_protocolo')
        atendimento = ProtocoloAtendimento.query.filter_by(numero_protocolo=numero_protocolo).first()

        if atendimento:
            return redirect(url_for('ver_atendimento', id=atendimento.id))
        else:
            flash("❌ Protocolo não encontrado. Verifique o número e tente novamente.", "error")
            return redirect(url_for('buscar_atendimento'))

    return render_template('buscar_atendimento.html')

# ================================
# ROTA 25: Visualizar Atendimento + Nova Resposta
# ================================
@app.route('/ver-atendimento/<int:id>', methods=['GET', 'POST'])
@login_required
def ver_atendimento(id):
    atendimento = ProtocoloAtendimento.query.get_or_404(id)

    if request.method == 'POST':
        resposta = request.form.get('resposta')

        if not resposta:
            flash("❌ A resposta não pode estar vazia.", "error")
            return redirect(url_for('ver_atendimento', id=id))

        nova_interacao = InteracaoAtendimento(
            id_atendimento=id,
            resposta=resposta,
            id_usuario=session['id_usuario']
        )
        db.session.add(nova_interacao)
        db.session.commit()
        flash("✅ Resposta adicionada com sucesso.", "success")
        return redirect(url_for('ver_atendimento', id=id))

    interacoes = InteracaoAtendimento.query.filter_by(id_atendimento=id).order_by(InteracaoAtendimento.data_hora.asc()).all()
    return render_template('ver_atendimento.html', atendimento=atendimento, interacoes=interacoes)

# ==================================================
# ROTA 26: Gerar Relatório Institucional SEI (.docx)
# ==================================================
@app.route('/gerar-relatorio-sei', methods=['GET'])
@login_required
def gerar_relatorio_sei_route():
    """
    Gera relatório institucional SEI-GDF (.docx)
    com base nos filtros e dados atualmente exibidos
    em Relatórios Avançados.
    """
    if not session.get('usuario'):
        return redirect(url_for('login'))

    from gerar_relatorio_sei import gerar_relatorio_sei

    dados = session.get('dados_relatorio', [])
    filtros = session.get('filtros_ativos', {})

    if not dados:
        flash("Nenhum dado disponível para gerar relatório SEI. Reaplique os filtros.", "warning")
        return redirect(url_for('relatorios_avancados'))

    df = pd.DataFrame(dados)
    autor = session['usuario']

    try:
        caminho_arquivo = gerar_relatorio_sei(df, filtros=filtros, autor=autor)
    except Exception as e:
        print(f"Erro ao gerar relatório SEI: {e}")
        abort(500, description="Erro interno ao gerar o relatório SEI-GDF.")

    return send_file(
        caminho_arquivo,
        as_attachment=True,
        download_name=os.path.basename(caminho_arquivo),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# ==================================================
# Execução do servidor
# ==================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
