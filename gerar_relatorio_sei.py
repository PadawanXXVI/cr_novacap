# ===========================================
# MÓDULO: gerar_relatorio_sei.py
# ===========================================
# Gera relatórios institucionais padronizados SEI-GDF (.docx)
# Emitido por: NOVACAP/PRES/CPCR
# Destinado a: Diretorias (DC, DO, DP, DS etc.)
# ===========================================

import pandas as pd
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime

# -------------------------------------------------------------
# Função principal
# -------------------------------------------------------------
def gerar_relatorio_sei(df: pd.DataFrame, filtros: dict, autor: str) -> str:
    """
    Gera um relatório Word (.docx) no padrão SEI-GDF.
    Emitido pela NOVACAP/PRES/CPCR com base em filtros aplicados.
    
    Parâmetros:
        df (pd.DataFrame): DataFrame com os dados filtrados
        filtros (dict): dicionário com status, RA, diretoria, datas etc.
        autor (str): nome de usuário que gerou o relatório
    Retorna:
        Caminho do arquivo gerado (.docx)
    """
    # ---------------------------------------------------------
    # 1️⃣ Início do documento
    # ---------------------------------------------------------
    doc = Document()

    # Define margens SEI (opcional)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(1.18)

    # ---------------------------------------------------------
    # 2️⃣ Cabeçalho institucional
    # ---------------------------------------------------------
    titulo = doc.add_paragraph()
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = titulo.add_run("Governo do Distrito Federal\n")
    run.bold = True
    run.font.size = Pt(12)

    run = titulo.add_run("Companhia Urbanizadora da Nova Capital do Brasil – NOVACAP\n")
    run.bold = True
    run.font.size = Pt(12)

    run = titulo.add_run("Comissão Permanente da Central de Relacionamento – CPCR")
    run.font.size = Pt(11)

    doc.add_paragraph("\n")  # espaçamento

    # ---------------------------------------------------------
    # 3️⃣ Identificação e assunto
    # ---------------------------------------------------------
    numero_relatorio = datetime.now().strftime("%m/%Y")
    doc.add_paragraph(f"Relatório nº {numero_relatorio} – NOVACAP/PRES/CPCR").bold = True
    data_br = datetime.now().strftime("%d de %B de %Y").capitalize()
    p_data = doc.add_paragraph(f"Brasília, {data_br}.")
    p_data.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    assunto = "Consolidação das Demandas"
    if filtros.get("status"):
        assunto += f" – Status: {filtros['status']}"
    if filtros.get("ra"):
        assunto += f" – RA: {filtros['ra']}"
    doc.add_paragraph(f"\nAssunto: {assunto}")
    doc.add_paragraph("Ilmo. Sr. Diretor-Presidente da NOVACAP,\n")

    # ---------------------------------------------------------
    # 4️⃣ SEÇÃO 1: CONTEXTO
    # ---------------------------------------------------------
    doc.add_paragraph("1. CONTEXTO").runs[0].bold = True
    p1 = doc.add_paragraph(
        "1.1. O presente relatório, elaborado pela Comissão Permanente da Central de Relacionamento (CPCR/PRES), "
        "tem por finalidade consolidar as informações referentes às solicitações registradas e tramitadas "
        "no Sistema de Controle de Processos e Protocolo de Atendimentos – SISTRAMITE, "
        "encaminhadas às Diretorias competentes da NOVACAP, conforme os filtros aplicados neste relatório."
    )
    p1.paragraph_format.space_after = Pt(8)

    # ---------------------------------------------------------
    # 5️⃣ SEÇÃO 2: RELATO
    # ---------------------------------------------------------
    doc.add_paragraph("2. RELATO").runs[0].bold = True

    if df.empty:
