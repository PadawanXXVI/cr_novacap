# -- coding: utf-8 --
"""
Sistema CR-NOVACAP — Controle de Processos e Atendimentos
Versão modularizada (Flask + MySQL)
"""

import os
from io import BytesIO
from datetime import datetime, timedelta

from flask import (
    Flask, render_template, request, redirect, url_for, flash, session,
    make_response, send_file, jsonify, abort
)
from flask_login import login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from sqlalchemy import or_

from app import create_app
from app.ext import db
from app.models.modelos import (
    Processo, EntradaProcesso, Demanda, TipoDemanda, RegiaoAdministrativa,
    Status, Usuario, Movimentacao, ProtocoloAtendimento, InteracaoAtendimento,
    Diretoria
)

# ==================================================
# APP SETUP
# ==================================================
app = create_app()

# Configuração de sessão
app.permanent_session_lifetime = timedelta(hours=1)


# ==================================================
# 1️⃣ Tela inicial
# ==================================================
@app.route('/')
def index():
    return render_template('index.html')


# ==================================================
# 2️⃣ Login com autenticação
# ==================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        senha = request.form.get('password')
        sistema = request.form.get('sistema')

        usuario = Usuario.query.filter_by(usuario=username).first()
        if not usuario:
            flash("Usuário não encontrado.", "error")
            return redirect(url_for('login'))

        if not check_password_hash(usuario.senha_hash, senha):
            flash("Senha incorreta.", "error")
            return redirect(url_for('login'))

        if not usuario.aprovado:
            flash("Acesso ainda não autorizado pelo administrador.", "warning")
            return redirect(url_for('login'))

        if usuario.bloqueado:
            flash("Usuário bloqueado. Contate o administrador.", "error")
            return redirect(url_for('login'))

        login_user(usuario)
        session['usuario'] = usuario.usuario
        session['is_admin'] = usuario.is_admin
        session['id_usuario'] = usuario.id_usuario

        if sistema == 'tramite':
            return redirect(url_for('dashboard_processos'))
        elif sistema == 'protocolo':
            return redirect(url_for('dashboard_protocolo'))
        else:
            flash("Selecione um módulo válido para acessar.", "warning")
            return redirect(url_for('login'))

    return render_template('login.html')


# ==================================================
# 3️⃣ Cadastro de Usuário
# ==================================================
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome_completo')
        email = request.form.get('email')
        usuario = request.form.get('username')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')

        if senha != confirmar_senha:
            flash("As senhas não coincidem.", "error")
            return redirect(url_for('cadastro'))

        existente = Usuario.query.filter(
            (Usuario.usuario == usuario) | (Usuario.email == email)
        ).first()
        if existente:
            flash("Usuário ou e-mail já cadastrado.", "warning")
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

        flash("✅ Cadastro enviado. Aguarde aprovação do administrador.", "success")
        return redirect(url_for('index'))

    return render_template('cadastro.html')


# ==================================================
# 4️⃣ Redefinir Senha
# ==================================================
@app.route('/trocar-senha', methods=['GET', 'POST'])
def trocar_senha():
    if request.method == 'POST':
        nome = request.form.get('nome_completo')
        email = request.form.get('email')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')

        if nova_senha != confirmar_senha:
            flash("As senhas não coincidem.", "error")
            return redirect(url_for('trocar_senha'))

        usuario = Usuario.query.filter_by(nome=nome, email=email).first()
        if not usuario:
            flash("Dados não encontrados.", "error")
            return redirect(url_for('trocar_senha'))

        usuario.senha_hash = generate_password_hash(nova_senha)
        db.session.commit()
        flash("Senha atualizada com sucesso.", "success")
        return redirect(url_for('login'))

    return render_template('trocar_senha.html')


# ==================================================
# 5️⃣ Dashboard de Processos
# ==================================================
@app.route('/dashboard-processos')
@login_required
def dashboard_processos():
    total_processos = Processo.query.count()
    processos_atendidos = Processo.query.filter_by(status_atual='Atendido').count()
    processos_dc = Processo.query.filter_by(diretoria_destino='Diretoria das Cidades - DC').count()
    processos_do = Processo.query.filter_by(diretoria_destino='Diretoria de Obras - DO').count()
    processos_dp = Processo.query.filter_by(diretoria_destino='Diretoria de Planejamento e Projetos - DP').count()
    processos_ouvidoria = Processo.query.filter_by(status_atual='Processo oriundo de Ouvidoria').count()

    return render_template(
        'dashboard_processos.html',
        total_processos=total_processos,
        processos_atendidos=processos_atendidos,
        processos_dc=processos_dc,
        processos_do=processos_do,
        processos_dp=processos_dp,
        processos_ouvidoria=processos_ouvidoria
    )


# ==================================================
# 6️⃣ Cadastro de Processo
# ==================================================
@app.route('/cadastro-processo', methods=['GET', 'POST'])
@login_required
def cadastro_processo():
    if request.method == 'POST':
        numero = request.form.get('numero_processo', '').strip()

        processo_existente = Processo.query.filter_by(numero_processo=numero).first()
        if processo_existente:
            flash("⚠ Processo já cadastrado.", "warning")
            return redirect(url_for('alterar_processo', id_processo=processo_existente.id_processo))

        try:
            data_criacao_ra = datetime.strptime(request.form.get('data_criacao_ra'), "%Y-%m-%d").date()
            data_entrada_novacap = datetime.strptime(request.form.get('data_entrada_novacap'), "%Y-%m-%d").date()
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
            return redirect(url_for('cadastro_processo'))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erro ao cadastrar processo: {str(e)}", "error")
            return redirect(url_for('cadastro_processo'))

    regioes = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra.asc()).all()
    tipos = TipoDemanda.query.order_by(TipoDemanda.descricao.asc()).all()
    demandas = Demanda.query.order_by(Demanda.descricao.asc()).all()
    status = Status.query.order_by(Status.descricao.asc()).all()
    usuarios = Usuario.query.filter_by(aprovado=True, bloqueado=False).order_by(Usuario.usuario.asc()).all()
    diretorias = Diretoria.query.order_by(Diretoria.nome_completo.asc()).all()

    return render_template(
        'cadastro_processo.html',
        regioes=regioes, tipos=tipos, demandas=demandas,
        status=status, usuarios=usuarios, diretorias=diretorias
    )


# ==================================================
# 7️⃣ Consulta Unificada (listar + visualizar)
# ==================================================
@app.route('/consultar-processos')
@login_required
def consultar_processos():
    if not session.get('usuario'):
        return redirect(url_for('login'))

    numero = request.args.get('numero_processo', '').strip()
    status_filtro = request.args.get('status')
    ra = request.args.get('ra')
    diretoria = request.args.get('diretoria')
    tipo = request.args.get('tipo')
    demanda = request.args.get('demanda')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    query = db.session.query(Processo).join(EntradaProcesso, Processo.id_processo == EntradaProcesso.id_processo)

    if numero:
        query = query.filter(Processo.numero_processo.like(f"%{numero}%"))
    if status_filtro:
        query = query.filter(Processo.status_atual == status_filtro)
    if ra:
        query = query.filter(EntradaProcesso.ra_origem == ra)
    if diretoria:
        query = query.filter(Processo.diretoria_destino == diretoria)
    if tipo:
        query = query.filter(EntradaProcesso.id_tipo == tipo)
    if demanda:
        query = query.filter(EntradaProcesso.id_demanda == demanda)
    if inicio and fim:
        query = query.filter(EntradaProcesso.data_entrada_novacap.between(inicio, fim))

    processos = query.order_by(Processo.id_processo.desc()).all()

    for p in processos:
        entrada = EntradaProcesso.query.filter_by(id_processo=p.id_processo).first()
        p.entrada = entrada
        if entrada:
            entrada.tipo = TipoDemanda.query.get(entrada.id_tipo)
            entrada.demanda = Demanda.query.get(entrada.id_demanda)
            ultima_mov = Movimentacao.query.filter_by(id_entrada=entrada.id_entrada).order_by(Movimentacao.data.desc()).first()
            p.ultima_data = ultima_mov.data if ultima_mov else entrada.data_documento

    todas_ras = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra).all()
    todos_status = Status.query.order_by(Status.ordem_exibicao).all()
    tipos = TipoDemanda.query.order_by(TipoDemanda.descricao.asc()).all()
    demandas = Demanda.query.order_by(Demanda.descricao.asc()).all()
    diretorias = [d.nome_completo for d in Diretoria.query.order_by(Diretoria.nome_completo.asc()).all()]

    return render_template(
        "consultar_processos.html",
        processos=processos,
        todas_ras=todas_ras,
        todos_status=todos_status,
        tipos=tipos,
        demandas=demandas,
        diretorias=diretorias
    )


# ==================================================
# 8️⃣ Painel Administrativo
# ==================================================
@app.route('/painel-admin')
@login_required
def painel_admin():
    if not session.get('is_admin'):
        return "Acesso restrito.", 403
    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return render_template('painel-admin.html', usuarios=usuarios)


# ==================================================
# 9️⃣ Logout
# ==================================================
@app.route('/logout')
def logout():
    session.clear()
    flash("Sessão encerrada com sucesso.", "info")
    return redirect(url_for('login'))


# ==================================================
# EXECUÇÃO
# ==================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
