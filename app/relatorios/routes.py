# ==========================================================
# 🔎 RELATÓRIO AVANÇADO — COMPLETO E CORRIGIDO
# ==========================================================
@relatorios_bp.route('/avancados')
@login_required
def relatorios_avancados():

    # ---------------------------------------------
    # LISTAS PARA OS SELECTS DO HTML
    # ---------------------------------------------
    todos_status = Status.query.order_by(Status.ordem_exibicao).all()
    todas_ras = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra).all()
    todas_demandas = Demanda.query.order_by(Demanda.descricao.asc()).all()
    todas_diretorias = Diretoria.query.order_by(Diretoria.descricao_exibicao).all()
    todos_departamentos = Departamento.query.order_by(Departamento.nome).all()

    # ---------------------------------------------
    # FILTROS RECEBIDOS
    # ---------------------------------------------
    status_sel = request.args.get("status")
    ra_sel = request.args.get("ra")
    diretoria_sel = request.args.get("diretoria")
    departamento_sel = request.args.get("departamento")
    demanda_sel = request.args.get("servico")
    inicio = request.args.get("inicio")
    fim = request.args.get("fim")

    # ---------------------------------------------
    # QUERY BASE (AGORA COMPLETA COM TODOS JOINS)
    # ---------------------------------------------
    query = (
        db.session.query(
            Movimentacao,
            Usuario,
            EntradaProcesso,
            Processo,
            Demanda,
            Departamento,
            Diretoria
        )
        .join(Usuario, Movimentacao.id_usuario == Usuario.id_usuario)
        .join(EntradaProcesso, Movimentacao.id_entrada == EntradaProcesso.id_entrada)
        .join(Processo, EntradaProcesso.id_processo == Processo.id_processo)
        .join(Demanda, EntradaProcesso.id_demanda == Demanda.id_demanda)
        .join(Departamento, Demanda.id_departamento == Departamento.id_departamento)
        .join(Diretoria, Departamento.id_diretoria == Diretoria.id_diretoria)
    )

    # ---------------------------------------------
    # APLICAÇÃO INTELIGENTE DOS FILTROS
    # ---------------------------------------------

    # 1) Diretoria
    if diretoria_sel:
        query = query.filter(Diretoria.descricao_exibicao == diretoria_sel)

    # 2) Departamento
    if departamento_sel:
        query = query.filter(Departamento.nome == departamento_sel)

    # 3) Demanda
    if demanda_sel:
        query = query.filter(Demanda.descricao == demanda_sel)

    # 4) Região Administrativa
    if ra_sel:
        query = query.filter(EntradaProcesso.ra_origem == ra_sel)

    # 5) Status
    if status_sel:
        query = query.filter(Movimentacao.novo_status == status_sel)

    # 6) Intervalo de Datas
    if inicio and fim:
        try:
            dt_inicio = datetime.strptime(inicio, "%Y-%m-%d")
            dt_fim = datetime.strptime(fim, "%Y-%m-%d")
            query = query.filter(Movimentacao.data.between(dt_inicio, dt_fim))
        except ValueError:
            flash("Formato de data inválido. Use AAAA-MM-DD.", "warning")

    # ---------------------------------------------
    # EXECUTA CONSULTA
    # ---------------------------------------------
    resultados = query.order_by(Movimentacao.data.desc()).all()

    # ---------------------------------------------
    # MONTA DATAFRAME COMPLETO PARA GRÁFICOS
    # ---------------------------------------------
    dados = []
    ras_distintas = set()
    demandas_distintas = set()

    for mov, user, entrada, processo, demanda, departamento, diretoria in resultados:

        dados.append({
            "Data": mov.data.strftime("%d/%m/%Y %H:%M"),
            "Número do Processo": processo.numero_processo,
            "RA": entrada.ra_origem,
            "Status": mov.novo_status,
            "Diretoria": diretoria.descricao_exibicao,
            "Departamento": departamento.nome,
            "Serviço": demanda.descricao,
            "Responsável": user.usuario,
            "Observação": mov.observacao or ""
        })

        ras_distintas.add(entrada.ra_origem)
        demandas_distintas.add(demanda.descricao)

    df = pd.DataFrame(dados)
    session["dados_relatorio"] = df.to_dict(orient="records")

    # =============================================
    # TOTAIS PARA OS CARDS
    # =============================================
    total_resultados = len(df)
    total_ras = len(ras_distintas)
    total_demandas = len(demandas_distintas)

    # ---------------------------------------------
    # RENDERIZA TEMPLATE
    # ---------------------------------------------
    return render_template(
        "relatorios_avancados.html",
        todos_status=todos_status,
        todas_ras=todas_ras,
        todas_demandas=todas_demandas,
        todas_diretorias=todas_diretorias,
        todos_departamentos=todos_departamentos,
        resultados=resultados,
        total_resultados=total_resultados,
        total_ras=total_ras,
        total_demandas=total_demandas
    )
