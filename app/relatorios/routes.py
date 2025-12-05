# app/relatorios/routes.py
from datetime import datetime
from io import BytesIO
import pandas as pd

from flask import (
    render_template, request, redirect, url_for, flash, session,
    send_file, make_response
)
from flask_login import login_required

from app.ext import db
from app.models.modelos import (
    Movimentacao,
    Usuario,
    EntradaProcesso,
    Processo,
    Demanda,
    Status,
    RegiaoAdministrativa,
    Diretoria,
    Departamento
)

from app.relatorios import relatorios_bp


# ==========================================================
# 🔎 RELATÓRIO AVANÇADO COMPLETO
# ==========================================================
@relatorios_bp.route('/avancados')
@login_required
def relatorios_avancados():

    # ---------------------------------------------
    # LISTAS PARA SELECTS DO HTML
    # ---------------------------------------------
    todos_status = Status.query.order_by(Status.ordem_exibicao).all()
    todas_ras = RegiaoAdministrativa.query.order_by(RegiaoAdministrativa.descricao_ra).all()
    todas_demandas = Demanda.query.order_by(Demanda.descricao.asc()).all()
    todas_diretorias = Diretoria.query.order_by(Diretoria.descricao_exibicao).all()
    todos_departamentos = Departamento.query.order_by(Departamento.nome).all()

    # ---------------------------------------------
    # FILTROS DO HTML
    # ---------------------------------------------
    status_sel = request.args.get("status")
    ra_sel = request.args.get("ra")
    diretoria_sel = request.args.get("diretoria")
    departamento_sel = request.args.get("departamento")
    demanda_sel = request.args.get("servico")
    inicio = request.args.get("inicio")
    fim = request.args.get("fim")

    # ---------------------------------------------
    # QUERY BASE (JOIN COMPLETO ENTRE AS TABELAS)
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

    # Filtro 1 — Diretoria
    if diretoria_sel:
        query = query.filter(Diretoria.descricao_exibicao == diretoria_sel)

    # Filtro 2 — Departamento
    if departamento_sel:
        query = query.filter(Departamento.nome == departamento_sel)

    # Filtro 3 — Demanda
    if demanda_sel:
        query = query.filter(Demanda.descricao == demanda_sel)

    # Filtro 4 — Região Administrativa
    if ra_sel:
        query = query.filter(EntradaProcesso.ra_origem == ra_sel)

    # Filtro 5 — Status
    if status_sel:
        query = query.filter(Movimentacao.novo_status == status_sel)

    # Filtro 6 — Datas
    if inicio and fim:
        try:
            dt_inicio = datetime.strptime(inicio, "%Y-%m-%d")
            dt_fim = datetime.strptime(fim, "%Y-%m-%d")
            query = query.filter(Movimentacao.data.between(dt_inicio, dt_fim))
        except ValueError:
            flash("Formato de data inválido. Use AAAA-MM-DD.", "warning")

    # ---------------------------------------------
    # EXECUTA QUERY
    # ---------------------------------------------
    resultados = query.order_by(Movimentacao.data.desc()).all()

    # ---------------------------------------------
    # MONTA DATAFRAME PARA GRÁFICOS E EXPORTAÇÃO
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

    # Totais dos cards
    total_resultados = len(df)
    total_ras = len(ras_distintas)
    total_demandas = len(demandas_distintas)

    # ---------------------------------------------
    # RENDERIZA HTML
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


# ==========================================================
# 📄 EXPORTAÇÃO CSV / XLSX — TOTALMENTE FUNCIONAL
# ==========================================================
@relatorios_bp.route('/exportar')
@login_required
def exportar_relatorios():

    dados = session.get("dados_relatorio", [])

    if not dados:
        flash("Nenhum dado disponível para exportação.", "warning")
        return redirect(url_for("relatorios_bp.relatorios_avancados"))

    df = pd.DataFrame(dados)
    formato = request.args.get("formato", "csv").lower()
    nome = f"Relatorio_Avancado_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # -------- XLSX --------
    if formato == "xlsx":
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Relatório")
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name=f"{nome}.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # -------- CSV --------
    csv = df.to_csv(index=False, sep=";", encoding="utf-8-sig")
    response = make_response(csv)
    response.headers["Content-Disposition"] = f"attachment; filename={nome}.csv"
    response.headers["Content-Type"] = "text/csv"
    return response
