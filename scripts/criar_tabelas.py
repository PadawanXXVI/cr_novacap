import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.__init__ import create_app
from app.models.modelos import db, Status, TipoDemanda, RegiaoAdministrativa, Demanda

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    
    # ------------------
    # TIPOS DE DEMANDA
    # ------------------
    tipos = ["Zeladoria", "Implantação", "Indivíduo Arbóreo"]
    for descricao in tipos:
        db.session.add(TipoDemanda(descricao=descricao))

    # ------------------
    # STATUS
    # ------------------
    status_lista = [
        ("Devolvido à RA de origem – adequação de requisitos", 1, False),
        ("Devolvido à RA de origem – parecer técnico de outro órgão", 2, False),
        ("Devolvido à RA de origem – serviço com contrato de natureza continuada pela DC/DO", 3, False),
        ("Devolvido à RA de origem – implantação", 4, False),
        ("Enviado à Diretoria das Cidades", 5, False),
        ("Enviado à Diretoria de Obras", 6, False),
        ("Improcedente – tramitação via SGIA", 7, False),
        ("Improcedente – tramita por órgão diferente da NOVACAP", 8, False),
        ("Encerrado pela RA de origem", 9, True),
        ("Atendido", 10, True)
    ]
    for descricao, ordem, finaliza in status_lista:
        db.session.add(Status(descricao=descricao, ordem_exibicao=ordem, finaliza_processo=finaliza))

    # ------------------
    # REGIÕES ADMINISTRATIVAS
    # ------------------
    regioes = [
        ("RA I", "Plano Piloto"),
        ("RA II", "Gama"),
        ("RA III", "Taguatinga"),
        ("RA IV", "Brazlândia"),
        ("RA V", "Sobradinho"),
        ("RA VI", "Planaltina"),
        ("RA VII", "Paranoá"),
        ("RA VIII", "Núcleo Bandeirante"),
        ("RA IX", "Ceilândia"),
        ("RA X", "Guará"),
        ("RA XI", "Cruzeiro"),
        ("RA XII", "Samambaia"),
        ("RA XIII", "Santa Maria"),
        ("RA XIV", "São Sebastião"),
        ("RA XV", "Recanto das Emas"),
        ("RA XVI", "Lago Sul"),
        ("RA XVII", "Riacho Fundo"),
        ("RA XVIII", "Lago Norte"),
        ("RA XIX", "Candangolândia"),
        ("RA XX", "Águas Claras"),
        ("RA XXI", "Riacho Fundo II"),
        ("RA XXII", "Sudoeste/Octogonal"),
        ("RA XXIII", "Varjão"),
        ("RA XXIV", "Park Way"),
        ("RA XXV", "SCIA – Estrutural"),
        ("RA XXVI", "Sobradinho II"),
        ("RA XXVII", "Jardim Botânico"),
        ("RA XXVIII", "Itapoã"),
        ("RA XXIX", "SIA"),
        ("RA XXX", "Vicente Pires"),
        ("RA XXXI", "Fercal"),
        ("RA XXXII", "Sol Nascente/Pôr do Sol"),
        ("RA XXXIII", "Arniqueira"),
        ("RA XXXIV", "Pôr do Sol/Sol Nascente"),
        ("RA XXXV", "Águas Claras Norte")
    ]
    for codigo, nome in regioes:
        descricao = f"{nome} ({codigo})"
        db.session.add(RegiaoAdministrativa(codigo_ra=codigo, nome_ra=nome, descricao_ra=descricao))

    # ------------------
    # DEMANDAS
    # ------------------
    demandas = [
        "Alambrado (Cercamento)", "Boca de Lobo", "Bueiro", "Calçada", "Doação de Mudas",
        "Estacionamentos", "Galeria de Águas Pluviais", "Jardim", "Mato Alto", "Meio-fio",
        "Parque Infantil", "Passagem Subterrânea", "Passarela", "Pisos Articulados",
        "Pista de Skate", "Poda / Supressão de Árvore", "Ponto de Encontro Comunitário (PEC)",
        "Praça", "Quadra de Esporte", "Rampa", "Recapeamento Asfáltico", "Tapa-buraco"
    ]
    for d in demandas:
        db.session.add(Demanda(descricao=d))

    db.session.commit()
    print("✅ Banco criado e tabelas populadas com sucesso!")
