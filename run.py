from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app
from app.ext import db
from app.models.modelos import Processo, EntradaProcesso, Demanda, TipoDemanda, RegiaoAdministrativa, Status, Usuario, Movimentacao
from datetime import datetime
import pandas as pd
from io import BytesIO
from flask_login import login_required, login_user

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

        # ✅ LOGIN FLASK-LOGIN
        login_user(usuario)

        # (opcional) manter compatibilidade com session manual
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
            flash("Erro: as senhas não coincidem.")
            return redirect(url_for('trocar_senha'))

        usuario = Usuario.query.filter_by(nome=nome, email=email).first()

        if usuario:
            usuario.senha_hash = generate_password_hash(nova_senha)
            db.session.commit()
            flash("Senha atualizada com sucesso! Faça login com sua nova senha.")
            return redirect(url_for('login'))
        else:
            flash("Erro: dados não encontrados. Verifique o nome e e-mail informados.")
            return redirect(url_for('trocar_senha'))

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

    # 1. Total de processos
    total_processos = Processo.query.count()

    # 2. Processos com status "Atendido"
    processos_atendidos = Processo.query.filter_by(status_atual='Atendido').count()

    # 3. Processos iniciados pela SECRE
    processos_secre = EntradaProcesso.query.filter_by(tramite_inicial='SECRE').count()

    # 4. Processos iniciados pela CR
    processos_cr = EntradaProcesso.query.filter_by(tramite_inicial='CR').count()

    # 5. Diretoria das Cidades – status atual
    processos_dc = Processo.query.filter_by(status_atual='Enviado à Diretoria das Cidades').count()

    # 6. Diretoria de Obras – status atual
    processos_do = Processo.query.filter_by(status_atual='Enviado à Diretoria de Obras').count()

    # 7. Total em atendimento (status atual em uma das diretorias)
    total_em_atendimento = processos_dc + processos_do

    # 8. Processos SGIA
    processos_sgia = Processo.query.filter_by(status_atual='Improcedente – tramitação via SGIA').count()

    # 9. Improcedentes – que tramitam por outro órgão
    processos_improcedentes = Processo.query.filter_by(
        status_atual='Improcedente – tramita por órgão diferente da NOVACAP'
    ).count()

    # 10. Devolvidos à RA (exceto improcedente)
    devolvidos_ra = Processo.query.filter(
        Processo.status_atual.in_([
            "Devolvido à RA de origem – adequação de requisitos",
            "Devolvido à RA de origem – parecer técnico de outro órgão",
            "Devolvido à RA de origem – serviço com contrato de natureza continuada pela DC/DO",
            "Devolvido à RA de origem – implantação"
        ])
    ).count()

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
                           devolvidos_ra=devolvidos_ra)

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

        # 🔍 Verifica se o processo já existe
        processo_existente = Processo.query.filter_by(numero_processo=numero).first()
        if processo_existente:
            flash("⚠️ Processo já cadastrado. Redirecionando para alteração...", "warning")
            return redirect(url_for('alterar_processo', id_processo=processo_existente.id_processo))

        try:
            # 📅 Conversão de datas
            data_criacao_ra = datetime.strptime(request.form.get('data_criacao_ra'), "%Y-%m-%d").date()
            data_entrada_novacap = datetime.strptime(request.form.get('data_entrada_novacap'), "%Y-%m-%d").date()
            data_documento = datetime.strptime(request.form.get('data_documento'), "%Y-%m-%d").date()

            # 📝 Criação do Processo
            novo_processo = Processo(
                numero_processo=numero,
                status_atual=request.form.get('status_inicial'),
                observacoes=request.form.get('observacoes'),
                diretoria_destino=request.form.get('diretoria_destino')
            )
            db.session.add(novo_processo)
            db.session.flush()  # Garante que o ID esteja disponível para a EntradaProcesso

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
            db.session.commit()

            flash("✅ Processo cadastrado com sucesso!", "success")
            return redirect(url_for('cadastro_processo'))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erro ao cadastrar processo: {str(e)}", "error")
            return redirect(url_for('cadastro_processo'))

    # GET: carrega os dados para os selects
    regioes = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra.asc()).all()
    tipos = TipoDemanda.query.order_by(TipoDemanda.descricao.asc()).all()
    demandas = Demanda.query.order_by(Demanda.descricao.asc()).all()
    status = Status.query.order_by(Status.ordem_exibicao.asc()).all()
    usuarios = Usuario.query.filter_by(aprovado=True, bloqueado=False).order_by(Usuario.usuario.asc()).all()

    diretorias = [
        "Diretoria das Cidades - DC",
        "Diretoria de Obras - DO",
        "Não tramita na Novacap"
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
# ROTA 11: Visualizar Processo
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
# ROTA 12: Listar Processos
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
# ROTA 13: Alterar Processo
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
# ROTA 14: Relatórios Gerenciais
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
# ROTA 15: Exportação de Tramitações
# ===================================
@app.route('/exportar-tramitacoes')
def exportar_tramitacoes():
    if not session.get('usuario'):
        return redirect(url_for('login'))

    ra = request.args.get('ra')
    usuario = request.args.get('usuario')
    status = request.args.get('status')
    inicio = request.args.get('inicio')
    fim = request.args.get('fim')

    query = db.session.query(Movimentacao, Usuario, EntradaProcesso, Processo) \
        .join(Usuario, Movimentacao.id_usuario == Usuario.id_usuario) \
        .join(EntradaProcesso, Movimentacao.id_entrada == EntradaProcesso.id_entrada) \
        .join(Processo, EntradaProcesso.id_processo == Processo.id_processo)

    if ra:
        query = query.filter(EntradaProcesso.ra_origem == ra)
    if usuario:
        query = query.filter(Usuario.usuario == usuario)
    if status:
        query = query.filter(Movimentacao.novo_status == status)
    if inicio and fim:
        query = query.filter(Movimentacao.data.between(inicio, fim))

    resultados = query.order_by(Movimentacao.data.desc()).all()

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

    df = pd.DataFrame(dados)
    csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig')

    response = make_response(csv)
    response.headers["Content-Disposition"] = "attachment; filename=tramitacoes_filtradas.csv"
    response.headers["Content-Type"] = "text/csv"
    return response

# ================================
# ROTA 16: Tornar usuário admin
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
# ROTA 17: Bloquear usuário
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
# Execução do servidor
# ================================
if __name__ == '__main__':
    app.run(debug=True)
