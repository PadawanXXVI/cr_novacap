# app/protocolo/routes.py
"""
Rotas do módulo de Protocolo (atendimentos) — CR-NOVACAP.
Inclui: dashboard, cadastro, listagem, busca e visualização com interações.
"""

from datetime import datetime

from flask import (
    render_template, request, redirect, url_for, flash, session
)
from flask_login import login_required

from app.ext import db
from app.models.modelos import (
    ProtocoloAtendimento, InteracaoAtendimento,
    RegiaoAdministrativa, Demanda
)
from app.protocolo import protocolo_bp


# ==========================================================
# 1️⃣ Dashboard de Protocolo
# ==========================================================
@protocolo_bp.route('/dashboard')
@login_required
def dashboard_protocolo():
    if not session.get('usuario'):
        return redirect(url_for('main_bp.login'))
    return render_template('dashboard_protocolo.html')


# ==========================================================
# 2️⃣ Cadastro de Atendimento
# ==========================================================
@protocolo_bp.route('/cadastro', methods=['GET', 'POST'])
@login_required
def cadastro_atendimento():
    if request.method == 'POST':
        try:
            atendimento = ProtocoloAtendimento(
                data_hora=datetime.now(),
                numero_protocolo=None,  # gerado após flush
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
            db.session.flush()  # garante ID para montar o número

            ano = atendimento.data_hora.year
            atendimento.numero_protocolo = f"CR-{atendimento.id:04d}/{ano}"

            db.session.commit()
            flash(f"✅ Atendimento registrado com protocolo {atendimento.numero_protocolo}", "success")
            return redirect(url_for('protocolo_bp.cadastro_atendimento'))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erro ao registrar atendimento: {str(e)}", "error")
            return redirect(url_for('protocolo_bp.cadastro_atendimento'))

    # GET — listas para os selects
    ras = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra.asc()).all()
    demandas = Demanda.query.order_by(Demanda.descricao.asc()).all()
    return render_template("cadastro_atendimento.html", ras=ras, demandas=demandas)


# ==========================================================
# 3️⃣ Listar Atendimentos
# ==========================================================
@protocolo_bp.route('/listar')
@login_required
def listar_atendimentos():
    atendimentos = ProtocoloAtendimento.query.order_by(ProtocoloAtendimento.data_hora.desc()).all()
    return render_template('listar_atendimentos.html', atendimentos=atendimentos)


# ==========================================================
# 4️⃣ Buscar Atendimento (por número de protocolo)
# ==========================================================
@protocolo_bp.route('/buscar', methods=['GET', 'POST'])
@login_required
def buscar_atendimento():
    if request.method == 'POST':
        numero_protocolo = request.form.get('numero_protocolo', '').strip()
        atendimento = ProtocoloAtendimento.query.filter_by(numero_protocolo=numero_protocolo).first()

        if atendimento:
            return redirect(url_for('protocolo_bp.ver_atendimento', id=atendimento.id))
        else:
            flash("❌ Protocolo não encontrado. Verifique o número e tente novamente.", "error")
            return redirect(url_for('protocolo_bp.buscar_atendimento'))

    return render_template('buscar_atendimento.html')


# ==========================================================
# 5️⃣ Visualizar Atendimento + Incluir Interação (resposta)
# ==========================================================
@protocolo_bp.route('/ver/<int:id>', methods=['GET', 'POST'])
@login_required
def ver_atendimento(id: int):
    atendimento = ProtocoloAtendimento.query.get_or_404(id)

    if request.method == 'POST':
        resposta = request.form.get('resposta', '').strip()
        if not resposta:
            flash("❌ A resposta não pode estar vazia.", "error")
            return redirect(url_for('protocolo_bp.ver_atendimento', id=id))

        try:
            nova_interacao = InteracaoAtendimento(
                id_atendimento=id,
                resposta=resposta,
                id_usuario=session['id_usuario']
            )
            db.session.add(nova_interacao)
            db.session.commit()
            flash("✅ Resposta adicionada com sucesso.", "success")
            return redirect(url_for('protocolo_bp.ver_atendimento', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erro ao salvar a resposta: {str(e)}", "error")
            return redirect(url_for('protocolo_bp.ver_atendimento', id=id))

    interacoes = (InteracaoAtendimento.query
                  .filter_by(id_atendimento=id)
                  .order_by(InteracaoAtendimento.data_hora.asc())
                  .all())

    return render_template('ver_atendimento.html', atendimento=atendimento, interacoes=interacoes)

