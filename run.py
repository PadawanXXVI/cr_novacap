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
# Execução do servidor
# ================================
if __name__ == '__main__':
    app.run(debug=True)
