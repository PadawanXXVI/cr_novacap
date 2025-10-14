# app/admin/routes.py
"""
Rotas do módulo administrativo — CR-NOVACAP.
Inclui painel de usuários, aprovação, bloqueio e atribuição de permissões.
"""

from flask import render_template, redirect, url_for, flash, session
from flask_login import login_required

from app.ext import db
from app.models.modelos import Usuario
from app.admin import admin_bp


# ==========================================================
# 1️⃣ Painel Administrativo
# ==========================================================
@admin_bp.route('/painel')
@login_required
def painel_admin():
    """Exibe o painel com a lista de usuários cadastrados"""
    if not session.get('is_admin'):
        flash("Acesso restrito ao administrador.", "error")
        return redirect(url_for('main_bp.login'))

    usuarios = Usuario.query.order_by(Usuario.nome.asc()).all()
    return render_template('painel_admin.html', usuarios=usuarios)


# ==========================================================
# 2️⃣ Aprovar Usuário
# ==========================================================
@admin_bp.route('/aprovar/<int:id_usuario>', methods=['POST'])
@login_required
def aprovar_usuario(id_usuario):
    """Aprova o cadastro de um novo usuário"""
    if not session.get('is_admin'):
        flash("Acesso restrito ao administrador.", "error")
        return redirect(url_for('main_bp.login'))

    usuario = Usuario.query.get_or_404(id_usuario)
    usuario.aprovado = True
    db.session.commit()

    flash(f"✅ Usuário '{usuario.usuario}' aprovado com sucesso.", "success")
    return redirect(url_for('admin_bp.painel_admin'))


# ==========================================================
# 3️⃣ Bloquear Usuário
# ==========================================================
@admin_bp.route('/bloquear/<int:id_usuario>', methods=['POST'])
@login_required
def bloquear_usuario(id_usuario):
    """Bloqueia um usuário ativo"""
    if not session.get('is_admin'):
        flash("Acesso restrito ao administrador.", "error")
        return redirect(url_for('main_bp.login'))

    usuario = Usuario.query.get_or_404(id_usuario)
    usuario.bloqueado = True
    db.session.commit()

    flash(f"🚫 Usuário '{usuario.usuario}' bloqueado.", "warning")
    return redirect(url_for('admin_bp.painel_admin'))


# ==========================================================
# 4️⃣ Desbloquear Usuário
# ==========================================================
@admin_bp.route('/desbloquear/<int:id_usuario>', methods=['POST'])
@login_required
def desbloquear_usuario(id_usuario):
    """Desbloqueia um usuário previamente bloqueado"""
    if not session.get('is_admin'):
        flash("Acesso restrito ao administrador.", "error")
        return redirect(url_for('main_bp.login'))

    usuario = Usuario.query.get_or_404(id_usuario)
    usuario.bloqueado = False
    db.session.commit()

    flash(f"✅ Usuário '{usuario.usuario}' desbloqueado.", "success")
    return redirect(url_for('admin_bp.painel_admin'))


# ==========================================================
# 5️⃣ Atribuir Permissão de Administrador
# ==========================================================
@admin_bp.route('/atribuir-admin/<int:id_usuario>', methods=['POST'])
@login_required
def atribuir_admin(id_usuario):
    """Concede permissão de administrador a um usuário"""
    if not session.get('is_admin'):
        flash("Acesso restrito ao administrador.", "error")
        return redirect(url_for('main_bp.login'))

    usuario = Usuario.query.get_or_404(id_usuario)
    usuario.is_admin = True
    db.session.commit()

    flash(f"👑 Usuário '{usuario.usuario}' agora é administrador.", "success")
    return redirect(url_for('admin_bp.painel_admin'))
