# app/main/routes.py
"""
Rotas principais do sistema CR-NOVACAP.
Inclui: tela inicial, login, cadastro, redefinição de senha e logout.
"""

from flask import (
    render_template, request, redirect, url_for, flash, session, jsonify
)
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app.ext import db
from app.models.modelos import Usuario
from app.main import main_bp


# ==========================================================
# 1️⃣ Tela inicial
# ==========================================================
@main_bp.route('/')
def index():
    """Página inicial pública"""
    return render_template('index.html')


# ==========================================================
# 2️⃣ Login de usuários
# ==========================================================
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Realiza login e direciona para o sistema selecionado"""
    if request.method == 'POST':
        username = request.form.get('username')
        senha = request.form.get('password')
        sistema = request.form.get('sistema')

        usuario = Usuario.query.filter_by(usuario=username).first()

        if not usuario:
            flash("Usuário não encontrado.", "error")
            return redirect(url_for('main_bp.login'))

        if not check_password_hash(usuario.senha_hash, senha):
            flash("Senha incorreta.", "error")
            return redirect(url_for('main_bp.login'))

        if not usuario.aprovado:
            flash("Acesso pendente de aprovação pelo administrador.", "warning")
            return redirect(url_for('main_bp.login'))

        if usuario.bloqueado:
            flash("Usuário bloqueado. Contate o administrador.", "error")
            return redirect(url_for('main_bp.login'))

        login_user(usuario)
        session['usuario'] = usuario.usuario
        session['is_admin'] = usuario.is_admin
        session['id_usuario'] = usuario.id_usuario

        flash(f"Bem-vindo, {usuario.nome}!", "success")

        if sistema == 'tramite':
            return redirect(url_for('processos_bp.dashboard_processos'))
        elif sistema == 'protocolo':
            return redirect(url_for('protocolo_bp.dashboard_protocolo'))
        else:
            flash("Sistema inválido selecionado.", "error")
            return redirect(url_for('main_bp.login'))

    return render_template('login.html')


# ==========================================================
# 3️⃣ Cadastro de novos usuários
# ==========================================================
@main_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Permite ao usuário solicitar cadastro no sistema"""
    if request.method == 'POST':
        nome = request.form.get('nome_completo')
        email = request.form.get('email')
        usuario = request.form.get('username')
        senha = request.form.get('senha')
        confirmar = request.form.get('confirmar_senha')

        if senha != confirmar:
            flash("As senhas não coincidem.", "error")
            return redirect(url_for('main_bp.cadastro'))

        existente = Usuario.query.filter(
            (Usuario.usuario == usuario) | (Usuario.email == email)
        ).first()
        if existente:
            flash("E-mail ou nome de usuário já cadastrado.", "error")
            return redirect(url_for('main_bp.cadastro'))

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

        flash("Cadastro enviado com sucesso. Aguarde aprovação do administrador.", "success")
        return redirect(url_for('main_bp.login'))

    return render_template('cadastro.html')


# ==========================================================
# 4️⃣ Redefinição de senha
# ==========================================================
@main_bp.route('/trocar-senha', methods=['GET', 'POST'])
def trocar_senha():
    """Permite redefinir senha a partir do nome e e-mail"""
    if request.method == 'POST':
        nome = request.form.get('nome_completo')
        email = request.form.get('email')
        nova_senha = request.form.get('nova_senha')
        confirmar = request.form.get('confirmar_senha')

        if nova_senha != confirmar:
            flash("As senhas não coincidem.", "error")
            return redirect(url_for('main_bp.trocar_senha'))

        usuario = Usuario.query.filter_by(nome=nome, email=email).first()
        if not usuario:
            flash("Usuário não encontrado com os dados informados.", "error")
            return redirect(url_for('main_bp.trocar_senha'))

        usuario.senha_hash = generate_password_hash(nova_senha)
        db.session.commit()

        flash("Senha alterada com sucesso. Faça login novamente.", "success")
        return redirect(url_for('main_bp.login'))

    return render_template('trocar_senha.html')


# ==========================================================
# 5️⃣ Logout
# ==========================================================
@main_bp.route('/logout')
@login_required
def logout():
    """Encerra sessão do usuário"""
    logout_user()
    session.clear()
    flash("Sessão encerrada com sucesso.", "info")
    return redirect(url_for('main_bp.login'))
