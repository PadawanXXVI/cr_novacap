from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
from app import create_app
from app.ext import db
from app.models.modelos import Usuario  # Certifique-se de que o modelo está correto

app = create_app()

# ================================
# ROTA 1: Tela inicial
# ================================
@app.route('/')
def index():
    return render_template('index.html')

# ================================
# ROTA 2: Login
# ================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        sistema = request.form.get('sistema')

        # Aqui virá a lógica de autenticação no futuro

        if sistema == 'tramite':
            return redirect(url_for('dashboard_processos'))
        elif sistema == 'protocolo':
            return redirect(url_for('dashboard_protocolo'))
        else:
            return "Sistema inválido", 400

    return render_template('login.html')

# ================================
# ROTA 3: Cadastro de usuário
# ================================
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        # Lógica de cadastro real será implementada depois
        return "Cadastro recebido. Aguardando autorização.", 200

    return render_template('cadastro.html')

# ================================
# ROTA 4: Redefinir senha
# ================================
@app.route('/trocar-senha', methods=['GET', 'POST'])
def trocar_senha():
    if request.method == 'POST':
        nome_completo = request.form.get('nome_completo')
        email = request.form.get('email')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')

        if nova_senha != confirmar_senha:
            return "Erro: as senhas não coincidem.", 400

        usuario = Usuario.query.filter_by(nome_completo=nome_completo, email=email).first()

        if usuario:
            usuario.senha = generate_password_hash(nova_senha)
            db.session.commit()
            return "Senha atualizada com sucesso!", 200
        else:
            return "Erro: dados não encontrados. Verifique as informações e tente novamente.", 404

    return render_template('trocar_senha.html')

# ================================
# ROTA 5: Dashboard de Processos
# ================================
@app.route('/dashboard-processos')
def dashboard_processos():
    return "<h2>Bem-vindo ao Sistema de Tramitação de Processos</h2>"

# ================================
# ROTA 6: Dashboard de Protocolo
# ================================
@app.route('/dashboard-protocolo')
def dashboard_protocolo():
    return "<h2>Bem-vindo ao Sistema de Protocolo de Atendimento</h2>"

# ================================
# Executar aplicação
# ================================
if __name__ == '__main__':
    app.run(debug=True)
