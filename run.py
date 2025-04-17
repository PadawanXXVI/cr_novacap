from flask import Flask, render_template, request, redirect, url_for
from app import create_app

app = create_app()

# ================================
# ROTA 1: Tela inicial
# ================================
@app.route('/')
def index():
    return render_template('index.html')

# ================================
# ROTA 2: Login (GET e POST)
# ================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        sistema = request.form.get('sistema')

        # Lógica futura de autenticação real (ainda não implementada)

        # Redirecionamento com base na escolha do sistema
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
        # Lógica de armazenamento será adicionada futuramente
        return "Cadastro recebido. Aguardando autorização.", 200

    return render_template('cadastro.html')

# ================================
# ROTA 4: Redefinir senha
# ================================
@app.route('/trocar-senha', methods=['GET', 'POST'])
def trocar_senha():
    if request.method == 'POST':
        # Lógica futura de redefinição de senha
        return "Senha redefinida com sucesso (placeholder)", 200

    return "<h2>Página de redefinição de senha em construção</h2>"

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
