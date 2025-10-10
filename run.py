from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, send_file, jsonify
from flask_login import login_required, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app
from app.ext import db
from app.models.modelos import Processo, EntradaProcesso, Demanda, TipoDemanda, RegiaoAdministrativa, Status, Usuario, Movimentacao, ProtocoloAtendimento, InteracaoAtendimento
from datetime import datetime
from io import BytesIO
import pandas as pd

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
# ROTA 5: Dashboard de Processos (ATUALIZADA)
# ================================
@app.route('/dashboard-processos')
def dashboard_processos():
    if not session.get('usuario'):
        return redirect(url_for('login'))

    total_processos = Processo.query.count()
    processos_atendidos = Processo.query.filter_by(status_atual='Atendido').count()
    processos_secre = EntradaProcesso.query.filter_by(tramite_inicial='SECRE').count()
    processos_cr = EntradaProcesso.query.filter_by(tramite_inicial='CR').count()
    processos_dc = Processo.query.filter_by(status_atual='Enviado à Diretoria das Cidades').count()
    processos_do = Processo.query.filter_by(status_atual='Enviado à Diretoria de Obras').count()
    total_em_atendimento = processos_dc + processos_do
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

    return render_template('dashboard_processos.html',
                           total_processos=total_processos,
                           processos_atendidos=processos_atendidos,
                           processos_secre=processos_secre,
                           processos_cr=processos_cr,
                           processos_dc=processos_dc,
                           processos_do=processos_do,
                           total_em_atendimento=total_em_atendimento,
                           processos_sgia=processos_sgia,
                           processos_improcedentes=processos_improcedentes,
                           devolvidos_ra=devolvidos_ra,
                           processos_urgentes=processos_urgentes,
                           processos_prazo_execucao=processos_prazo_execucao,
                           processos_ouvidoria=processos_ouvidoria)

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
        flash("❌ Processo não localizado. Deseja cadastrá-lo?", "error")
        return render_template('visualizar_processo.html', processo=None)

    entrada = EntradaProcesso.query.filter_by(id_processo=processo.id_processo).first()
    movimentacoes = []

    if entrada:
        entrada.tipo = TipoDemanda.query.get(entrada.id_tipo)
        entrada.responsavel = Usuario.query.get(entrada.usuario_responsavel)
        movimentacoes = db.session.query(Movimentacao).join(Usuario).filter(
            Movimentacao.id_entrada == entrada.id_entrada
        ).order_by(Movimentacao.data.asc()).all()

    ultima_observacao = (
        movimentacoes[-1].observacao if movimentacoes and movimentacoes[-1].observacao
        else processo.observacoes
    )

    return render_template(
        'visualizar_processo.html',
        processo=processo,
        entrada=entrada,
        movimentacoes=movimentacoes,
        ultima_observacao=ultima_observacao
    )

# ================================
# ROTA 7: Verificar Processo
# ================================
from flask import jsonify

@app.route('/verificar-processo', methods=['POST'])
def verificar_processo():
    data = request.get_json()
    numero = data.get('numero_processo')

    processo = Processo.query.filter_by(numero_processo=numero).first()

    if processo:
        return jsonify({"existe": True, "id": processo.id_processo})
    else:
        return jsonify({"existe": False})


# ================================
# ROTA 8: Cadastro de Processo
# ================================
from flask import render_template, request, redirect, url_for, flash, session
from datetime import datetime
from flask_login import login_required
from app.models.modelos import (
    Processo, EntradaProcesso, RegiaoAdministrativa,
    TipoDemanda, Demanda, Status, Usuario
)
from app.ext import db

@app.route('/cadastro-processo', methods=['GET', 'POST'])
@login_required
def cadastro_processo():
    if request.method == 'POST':
        numero = request.form.get('numero_processo').strip()

        processo_existente = Processo.query.filter_by(numero_processo=numero).first()
        if processo_existente:
            flash("⚠️ Processo já cadastrado. Redirecionando para alteração...", "warning")
            return redirect(url_for('alterar_processo', id_processo=processo_existente.id_processo))

        try:
            # Conversão de datas
            data_criacao_ra = datetime.strptime(request.form.get('data_criacao_ra'), "%Y-%m-%d").date()
            data_entrada_novacap = datetime.strptime(request.form.get('data_entrada_novacap'), "%Y-%m-%d").date()
            data_documento = datetime.strptime(request.form.get('data_documento'), "%Y-%m-%d").date()

            # Processo e entrada
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

            # Primeira movimentação
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
            return redirect(url_for('cadastro_processo'))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erro ao cadastrar processo: {str(e)}", "error")
            return redirect(url_for('cadastro_processo'))

    # 🔁 Se for GET, carrega os dados para o formulário
    regioes = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra.asc()).all()
    tipos = TipoDemanda.query.order_by(TipoDemanda.descricao.asc()).all()
    demandas = Demanda.query.order_by(Demanda.descricao.asc()).all()
    status = Status.query.order_by(Status.descricao.asc()).all()  # ✅ AGORA EM ORDEM ALFABÉTICA
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

# ================================
# ROTA 9: Listar Processos
# ================================
@app.route('/listar-processos')
def listar_processos():

    if not session.get('usuario'):
        return redirect(url_for('login'))

    # Filtros recebidos via GET
    status_filtro = request.args.get('status')
    ra = request.args.get('ra')
    diretoria = request.args.get('diretoria')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    # Base da query
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

    # Enriquecimento com dados relacionados
    for p in processos:
        entrada = EntradaProcesso.query.filter_by(id_processo=p.id_processo).first()
        p.entrada = entrada

        if entrada:
            entrada.tipo = TipoDemanda.query.get(entrada.id_tipo)
            entrada.movimentacoes = Movimentacao.query.filter_by(id_entrada=entrada.id_entrada).order_by(Movimentacao.data).all()

            # Atribui a última movimentação (ou data do documento)
            if entrada.movimentacoes:
                p.ultima_data = entrada.movimentacoes[-1].data
            else:
                p.ultima_data = entrada.data_documento

    # Dados para os filtros (selects)
    todos_status = Status.query.order_by(Status.ordem_exibicao).all()
    todas_ras = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra).all()

    return render_template("listar_processos.html",
                           processos=processos,
                           todos_status=todos_status,
                           todas_ras=todas_ras)

# ================================
# ROTA 10: Alterar Processo
# ================================
@app.route('/alterar-processo/<int:id_processo>', methods=['GET', 'POST'])
def alterar_processo(id_processo):
    if not session.get('usuario'):
        return redirect(url_for('login'))

    processo = Processo.query.get_or_404(id_processo)

    if request.method == 'POST':
        novo_status = request.form.get('novo_status')
        observacao = request.form.get('observacao')
        data_movimentacao = request.form.get('data_movimentacao')
        id_usuario = int(request.form.get('responsavel_tecnico'))

        if not (novo_status and observacao and data_movimentacao and id_usuario):
            flash("❌ Todos os campos são obrigatórios.", "error")
            return redirect(url_for('alterar_processo', id_processo=id_processo))

        responsavel = Usuario.query.get(id_usuario)
        if not responsavel:
            flash("❌ Responsável técnico não encontrado.", "error")
            return redirect(url_for('alterar_processo', id_processo=id_processo))

        entrada = EntradaProcesso.query.filter_by(id_processo=processo.id_processo).first()
        if not entrada:
            flash("❌ Entrada do processo não encontrada.", "error")
            return redirect(url_for('alterar_processo', id_processo=id_processo))

        try:
            data = datetime.strptime(data_movimentacao, "%Y-%m-%d")
        except ValueError:
            flash("❌ Data inválida. Use o formato correto (aaaa-mm-dd).", "error")
            return redirect(url_for('alterar_processo', id_processo=id_processo))

        nova_mov = Movimentacao(
            id_entrada=entrada.id_entrada,
            id_usuario=responsavel.id_usuario,
            novo_status=novo_status,
            observacao=observacao,
            data=data
        )
        db.session.add(nova_mov)

        processo.status_atual = novo_status
        db.session.commit()

        flash("✅ Processo alterado com sucesso!", "success")
        return redirect(url_for('dashboard_processos'))

    status = Status.query.order_by(Status.ordem_exibicao).all()
    usuarios = Usuario.query.order_by(Usuario.usuario).all()

    return render_template("alterar_processo.html",
                           processo=processo,
                           status=status,
                           usuarios=usuarios)

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
# ROTA 18: Relatórios Avançados (ATUALIZADA)
# ================================
@app.route('/relatorios-avancados')
def relatorios_avancados():
    if not session.get('usuario'):
        return redirect(url_for('login'))

    # Listas para filtros
    todos_status = Status.query.order_by(Status.ordem_exibicao).all()
    todas_ras = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra).all()
    usuarios = Usuario.query.filter_by(aprovado=True, bloqueado=False).order_by(Usuario.usuario).all()

    # Parâmetros de filtro
    status = request.args.get('status')
    ra = request.args.get('ra')
    usuario = request.args.get('usuario')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')
    modo_status = request.args.get('modo_status')  # novo parâmetro: "atual" ou "historico"

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

    return render_template(
        'relatorios_avancados.html',
        todos_status=todos_status,
        todas_ras=todas_ras,
        usuarios=usuarios,
        resultados=resultados,
        modo_status=modo_status  # passar para o template
    )

# ================================
# ROTA 19: Relatórios BI Interativo
# ================================
from flask import render_template, request, redirect, url_for, flash, session
from app.ext import db
from app.models.modelos import Processo, EntradaProcesso, Movimentacao
from datetime import datetime

@app.route('/relatorios-bi')
def relatorios_bi():
    if not session.get('usuario'):
        return redirect(url_for('login'))

    # ==== Filtros por período ====
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    try:
        if inicio:
            inicio_data = datetime.strptime(inicio, "%Y-%m-%d")
        else:
            inicio_data = None

        if fim:
            fim_data = datetime.strptime(fim, "%Y-%m-%d")
        else:
            fim_data = None
    except ValueError:
        flash("Formato de data inválido.", "error")
        return redirect(url_for('relatorios_bi'))

    # ==== Base para filtro ====
    def filtrar_datas(query, campo_data):
        if inicio_data and fim_data:
            return query.filter(campo_data.between(inicio_data, fim_data))
        return query

    # ==== Gráfico de Status ====
    status_query = db.session.query(Processo.status_atual, db.func.count(Processo.id_processo))
    status_query = filtrar_datas(status_query.join(EntradaProcesso), EntradaProcesso.data_entrada_novacap)
    status_data = status_query.group_by(Processo.status_atual).all()
    grafico_status = {
        "labels": [s[0] for s in status_data],
        "valores": [s[1] for s in status_data]
    }

    # ==== Gráfico de RA ====
    ra_query = db.session.query(EntradaProcesso.ra_origem, db.func.count(EntradaProcesso.id_entrada))
    ra_query = filtrar_datas(ra_query, EntradaProcesso.data_entrada_novacap)
    ra_data = ra_query.group_by(EntradaProcesso.ra_origem).all()
    grafico_ra = {
        "labels": [r[0] for r in ra_data],
        "valores": [r[1] for r in ra_data]
    }

    # ==== Gráfico de Diretorias ====
    todas_diretorias = [
        "Diretoria das Cidades - DC",
        "Diretoria de Obras - DO",
        "Diretoria de Planejamento e Projetos - DP",
        "Diretoria de Suporte - DS",
        "Não tramita na Novacap",
        "Tramita via SGIA"
    ]
    dir_query = db.session.query(Processo.diretoria_destino, db.func.count(Processo.id_processo)) \
        .join(EntradaProcesso)
    dir_query = filtrar_datas(dir_query, EntradaProcesso.data_entrada_novacap)
    dir_data = dir_query.group_by(Processo.diretoria_destino).all()
    dir_dict = {d[0]: d[1] for d in dir_data}
    grafico_diretoria = {
        "labels": todas_diretorias,
        "valores": [dir_dict.get(d, 0) for d in todas_diretorias]
    }

    # ==== Tempo médio de entrada ====
    entradas = EntradaProcesso.query
    entradas = filtrar_datas(entradas, EntradaProcesso.data_entrada_novacap).all()
    tempos_entrada = [
        (e.data_entrada_novacap - e.data_criacao_ra).days
        for e in entradas if e.data_criacao_ra and e.data_entrada_novacap
    ]
    tempo_medio_entrada = round(sum(tempos_entrada) / len(tempos_entrada), 1) if tempos_entrada else 0

    # ==== Tempo médio de atendimento ====
    processos_atendidos = Processo.query.filter_by(status_atual="Atendido").join(EntradaProcesso)
    processos_atendidos = filtrar_datas(processos_atendidos, EntradaProcesso.data_entrada_novacap).all()
    tempos_atendimento = []
    for p in processos_atendidos:
        entrada = EntradaProcesso.query.filter_by(id_processo=p.id_processo).first()
        if entrada:
            ultima_mov = Movimentacao.query.filter_by(id_entrada=entrada.id_entrada) \
                .order_by(Movimentacao.data.desc()).first()
            if ultima_mov and entrada.data_entrada_novacap:
                dias = (ultima_mov.data.date() - entrada.data_entrada_novacap).days
                tempos_atendimento.append(dias)

    tempo_medio_atendimento = round(sum(tempos_atendimento) / len(tempos_atendimento), 1) if tempos_atendimento else 0

    # ==== Totais ====
    total_processos = filtrar_datas(Processo.query.join(EntradaProcesso), EntradaProcesso.data_entrada_novacap).count()
    total_tramitacoes = filtrar_datas(Movimentacao.query.join(EntradaProcesso), EntradaProcesso.data_entrada_novacap).count()

    return render_template(
        "relatorios_bi.html",
        grafico_status=grafico_status,
        grafico_ra=grafico_ra,
        grafico_diretoria=grafico_diretoria,
        tempo_medio_entrada=tempo_medio_entrada,
        tempo_medio_atendimento=tempo_medio_atendimento,
        total_processos=total_processos,
        total_tramitacoes=total_tramitacoes
    )

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
from scripts.gerar_relatorio_sei import gerar_relatorio_sei  # ✅ Import da função correta

@app.route('/gerar-relatorio-sei', methods=['GET'])
@login_required
def gerar_relatorio_sei_route():
    """
    Gera relatório institucional no formato SEI-GDF (.docx)
    com base nos filtros aplicados na página de Relatórios Avançados.
    Emitido por: NOVACAP/PRES/CPCR
    Destinado a: Diretorias DC, DO, DP e DS.
    """
    if not session.get('usuario'):
        return redirect(url_for('login'))

    # 🔹 Lê filtros da query string (GET)
    filtros = request.args.to_dict()
    status = filtros.get('status')
    ra = filtros.get('ra')
    usuario = filtros.get('usuario')
    inicio = filtros.get('inicio')
    fim = filtros.get('fim')
    modo_status = filtros.get('modo_status', 'historico')

    # 🔹 Consulta replicando a base de relatorios_avancados
    query = (
        db.session.query(Movimentacao, Usuario, EntradaProcesso, Processo)
        .join(Usuario, Movimentacao.id_usuario == Usuario.id_usuario)
        .join(EntradaProcesso, Movimentacao.id_entrada == EntradaProcesso.id_entrada)
        .join(Processo, EntradaProcesso.id_processo == Processo.id_processo)
    )

    # 🔹 Filtros aplicados
    if status:
        query = (
            query.filter(Processo.status_atual == status)
            if modo_status == 'atual'
            else query.filter(Movimentacao.novo_status == status)
        )
    if ra:
        query = query.filter(EntradaProcesso.ra_origem == ra)
    if usuario:
        query = query.filter(Usuario.usuario == usuario)
    if inicio and fim:
        query = query.filter(Movimentacao.data.between(inicio, fim))

    resultados = query.order_by(Movimentacao.data.desc()).all()

    # 🔹 Monta o DataFrame
    dados = [
        {
            "Data": mov.data.strftime("%d/%m/%Y %H:%M"),
            "Número do Processo": processo.numero_processo,
            "RA": entrada.ra_origem,
            "Status": mov.novo_status,
            "Responsável": user.usuario,
            "Serviço": (
                TipoDemanda.query.get(entrada.id_tipo).descricao
                if entrada.id_tipo else ""
            ),
        }
        for mov, user, entrada, processo in resultados
    ]
    df = pd.DataFrame(dados)

    # 🔹 Gera o relatório institucional (SEI-GDF)
    caminho_arquivo = gerar_relatorio_sei(df, filtros=filtros, autor=session['usuario'])

    # 🔹 Retorna o .docx para download direto
    return send_file(
        caminho_arquivo,
        as_attachment=True,
        download_name=f"Relatorio_SEI_CPCR_{datetime.now().strftime('%Y%m%d')}.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# ==================================================
# Execução do servidor
# ==================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
