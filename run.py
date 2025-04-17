from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app
from app.ext import db
from app.models.modelos import Processo, EntradaProcesso, Demanda, TipoDemanda, RegiaoAdministrativa, Status, Usuario
from datetime import datetime

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

        # Armazena dados na sessão
        session['usuario'] = usuario.usuario
        session['is_admin'] = usuario.is_admin
        session['id_usuario'] = usuario.id_usuario

        # Redireciona conforme sistema escolhido
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
            return "Erro: as senhas não coincidem.", 400

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
        return "Cadastro realizado com sucesso. Aguarde aprovação do administrador.", 200

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
            return "Erro: as senhas não coincidem.", 400

        usuario = Usuario.query.filter_by(nome=nome, email=email).first()

        if usuario:
            usuario.senha_hash = generate_password_hash(nova_senha)
            db.session.commit()
            return "Senha atualizada com sucesso!", 200
        else:
            return "Erro: dados não encontrados.", 404

    return render_template('trocar_senha.html')

# ================================
# ROTA 5: Painel Administrativo
# ================================
@app.route('/painel-admin')
def painel_admin():
    if not session.get('is_admin'):
        return "Acesso restrito ao administrador.", 403

    usuarios = Usuario.query.filter_by(aprovado=False).all()
    return render_template('painel-admin.html', usuarios=usuarios)

# ================================
# ROTA 6: Aprovar Usuário
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
# ROTA 7: Dashboard de Processos
# ================================
@app.route('/dashboard-processos')
def dashboard_processos():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    return "<h2>Bem-vindo ao Sistema de Tramitação de Processos</h2>"

# ================================
# ROTA 8: Dashboard de Protocolo
# ================================
@app.route('/dashboard-protocolo')
def dashboard_protocolo():
    if not session.get('usuario'):
        return redirect(url_for('login'))
    return "<h2>Bem-vindo ao Sistema de Protocolo de Atendimento</h2>"

# ================================
# ROTA 9: Logout
# ================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# ================================
# ROTA 10: Cadastro de Processo
# ================================
@app.route('/cadastro-processo', methods=['GET', 'POST'])
def cadastro_processo():
    if request.method == 'POST':
        numero = request.form.get('numero_processo')

        if Processo.query.filter_by(numero_processo=numero).first():
            return "Erro: número de processo já cadastrado.", 400

        # Cria o processo principal
        novo_processo = Processo(
            numero_processo=numero,
            status_atual=request.form.get('status_inicial'),
            observacoes=request.form.get('observacoes')
        )
        db.session.add(novo_processo)
        db.session.flush()  # Garante que o ID do processo fique disponível

        entrada = EntradaProcesso(
            id_processo=novo_processo.id_processo,
            data_criacao_ra=request.form.get('data_criacao_ra'),
            data_entrada_novacap=request.form.get('data_entrada_novacap'),
            data_documento=request.form.get('data_documento'),
            tramite_inicial=request.form.get('tramite_inicial'),
            ra_origem=request.form.get('ra_origem'),
            id_tipo=int(request.form.get('id_tipo')),
            id_demanda=int(request.form.get('id_demanda')),
            usuario_responsavel=session.get('usuario'),
            status_inicial=request.form.get('status_inicial'),
            possui_vistoria='possui_vistoria' in request.form,
            oficio_assinado='oficio_assinado' in request.form,
            encerrado_pela_ra='encerrado_pela_ra' in request.form,
            data_encerramento_pela_ra=request.form.get('data_encerramento_pela_ra') or None
        )
        db.session.add(entrada)
        db.session.commit()

        return "✅ Processo cadastrado com sucesso!", 200

    # GET: busca dados para preencher selects
    regioes = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra).all()
    tipos = TipoDemanda.query.order_by(TipoDemanda.descricao).all()
    demandas = Demanda.query.order_by(Demanda.descricao).all()
    status = Status.query.order_by(Status.ordem_exibicao).all()

    return render_template('cadastro_processo.html', regioes=regioes, tipos=tipos, demandas=demandas, status=status)

# ================================
# ROTA 11: Cadastro de Demanda
# ================================
@app.route('/dashboard-processos')
def dashboard_processos():
    if not session.get('usuario'):
        return redirect(url_for('login'))

    # Aqui entrariam as consultas reais ao banco
    total_processos = Processo.query.count()
    processos_atendidos = Processo.query.filter(Processo.status_atual == 'Atendido').count()
    processos_secre = EntradaProcesso.query.filter_by(tramite_inicial='SECRE').count()
    processos_cr = EntradaProcesso.query.filter_by(tramite_inicial='CR').count()
    processos_dc = Processo.query.filter(Processo.status_atual.ilike('%Diretoria das Cidades%')).count()
    processos_do = Processo.query.filter(Processo.status_atual.ilike('%Diretoria de Obras%')).count()
    devolvidos_ra = Processo.query.filter(
    Processo.status_atual.in_([
        "Devolvido à RA de origem – adequação de requisitos",
        "Devolvido à RA de origem – parecer técnico de outro órgão",
        "Devolvido à RA de origem – serviço com contrato de natureza continuada pela DC/DO"
    ])
).count()
    processos_sgia = Processo.query.filter(Processo.status_atual.ilike('%SGIA%')).count()

    return render_template('dashboard_processos.html',
                           total_processos=total_processos,
                           processos_atendidos=processos_atendidos,
                           processos_secre=processos_secre,
                           processos_cr=processos_cr,
                           processos_dc=processos_dc,
                           processos_do=processos_do,
                           devolvidos_ra=devolvidos_ra,
                           processos_sgia=processos_sgia)

# ================================
# ROTA 12: Visualizar Processo
# ================================
@app.route('/visualizar-processo/<int:id_processo>')
def visualizar_processo(id_processo):
    if not session.get('usuario'):
        return redirect(url_for('login'))

    processo = Processo.query.get_or_404(id_processo)
    entrada = EntradaProcesso.query.filter_by(id_processo=processo.id_processo).first()

    # Join com usuário para mostrar no histórico
    movimentacoes = db.session.query(Movimentacao).join(Usuario).filter(
        Movimentacao.id_entrada == entrada.id_entrada if entrada else None
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
# ROTA 13: Listar Processos
# ================================
@app.route('/listar-processos')
def listar_processos():
    if not session.get('usuario'):
        return redirect(url_for('login'))

    numero = request.args.get('numero')
    status_filtro = request.args.get('status')

    query = Processo.query

    if numero:
        query = query.filter(Processo.numero_processo.ilike(f"%{numero}%"))
    if status_filtro:
        query = query.filter_by(status_atual=status_filtro)

    processos = query.order_by(Processo.id_processo.desc()).all()

    # Enriquecer com entrada, tipo, movimentações
    for p in processos:
        p.entrada = EntradaProcesso.query.filter_by(id_processo=p.id_processo).first()
        if p.entrada:
            p.entrada.tipo = TipoDemanda.query.get(p.entrada.id_tipo)
            p.entrada.movimentacoes = Movimentacao.query.filter_by(id_entrada=p.entrada.id_entrada).order_by(Movimentacao.data).all()

    todos_status = Status.query.order_by(Status.ordem_exibicao).all()

    return render_template("listar_processos.html", processos=processos, todos_status=todos_status)

# ================================
# ROTA 14: Alterar Processo
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
        usuario_nome = request.form.get('responsavel_tecnico')

        # Validação dos campos obrigatórios
        if not (novo_status and observacao and data_movimentacao and usuario_nome):
            return "Erro: Todos os campos são obrigatórios.", 400

        # Busca do responsável
        responsavel = Usuario.query.filter_by(usuario=usuario_nome).first()
        if not responsavel:
            return "Erro: responsável técnico não encontrado.", 404

        # Busca da entrada do processo
        entrada = EntradaProcesso.query.filter_by(id_processo=processo.id_processo).first()
        if not entrada:
            return "Erro: entrada do processo não encontrada.", 404

        # Criação da movimentação
        nova_mov = Movimentacao(
            id_entrada=entrada.id_entrada,
            id_usuario=responsavel.id_usuario,
            novo_status=novo_status,
            observacao=observacao,
            data=datetime.strptime(data_movimentacao, "%Y-%m-%d")
        )
        db.session.add(nova_mov)

        # Atualiza o status atual do processo
        processo.status_atual = novo_status
        db.session.commit()

        return redirect(url_for('dashboard_processos'))

    # GET – carrega lista de usuários e status
    status = Status.query.order_by(Status.ordem_exibicao).all()
    usuarios = Usuario.query.order_by(Usuario.usuario).all()

    return render_template("alterar_processo.html",
                           processo=processo,
                           status=status,
                           usuarios=usuarios)

# ================================
# ROTA 15: Relatórios Gerenciais
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

# =====================================
# ROTA 16: Exportar Processos para CSV
# =====================================
import pandas as pd
from flask import make_response

@app.route('/exportar-processos-csv')
def exportar_processos_csv():
    if not session.get('usuario'):
        return redirect(url_for('login'))

    numero = request.args.get('numero')
    status_filtro = request.args.get('status')

    query = Processo.query.join(EntradaProcesso)

    if numero:
        query = query.filter(Processo.numero_processo.ilike(f"%{numero}%"))
    if status_filtro:
        query = query.filter(Processo.status_atual == status_filtro)

    processos = query.all()

    dados = []
    for p in processos:
        entrada = EntradaProcesso.query.filter_by(id_processo=p.id_processo).first()
        tipo = TipoDemanda.query.get(entrada.id_tipo) if entrada else None

        dados.append({
            "Número do Processo": p.numero_processo,
            "Status Atual": p.status_atual,
            "RA de Origem": entrada.ra_origem if entrada else '',
            "Tipo de Demanda": tipo.descricao if tipo else '',
            "Data de Entrada": entrada.data_entrada_novacap.strftime('%d/%m/%Y') if entrada else '',
        })

    df = pd.DataFrame(dados)
    csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig')

    response = make_response(csv)
    response.headers["Content-Disposition"] = "attachment; filename=processos_exportados.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

# ================================
# Execução do servidor
# ================================
if __name__ == '__main__':
    app.run(debug=True)
