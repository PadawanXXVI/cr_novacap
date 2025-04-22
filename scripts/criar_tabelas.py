import sys
import os
from dotenv import load_dotenv

# 🟢 Carrega variáveis do .env antes de qualquer configuração
load_dotenv()

# 🛠 Ajusta o path para garantir importações corretas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 🔧 Cria o app com configurações do .env
from app import create_app
app = create_app()

# 🧪 Mostra qual banco está conectado
print("🔍 URI ativa:", app.config['SQLALCHEMY_DATABASE_URI'])

# 📦 Importa extensões e modelos necessários para a criação
from app.ext import db
from app.models.modelos import (
    Status, TipoDemanda, RegiaoAdministrativa, Demanda,
    ProtocoloAtendimento, InteracaoAtendimento
)

with app.app_context():
    # ✅ Cria apenas as tabelas que ainda não existem
    db.create_all()

    # ------------------
    # TIPOS DE DEMANDA
    # ------------------
    tipos = sorted(["Zeladoria", "Implantação", "Indivíduo Arbóreo"])
    for descricao in tipos:
        if not TipoDemanda.query.filter_by(descricao=descricao).first():
            db.session.add(TipoDemanda(descricao=descricao))

    # ------------------
    # STATUS
    # ------------------
    status_lista = sorted([
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
    ], key=lambda x: x[0])

    for descricao, ordem, finaliza in status_lista:
        if not Status.query.filter_by(descricao=descricao).first():
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
        ("RA XXXIV", "Arapoanga"),
        ("RA XXXV", "Água Quente")
    ]

    for codigo, nome in regioes:
        descricao = f"{nome} ({codigo})"
        if not RegiaoAdministrativa.query.filter_by(codigo_ra=codigo).first():
            db.session.add(RegiaoAdministrativa(codigo_ra=codigo, nome_ra=nome, descricao_ra=descricao))

    # ------------------
    # DEMANDAS
    # ------------------
    demandas = [
        "Alambrado (Cercamento)", "Boca de Lobo", "Bueiro", "Calçada", "Doação de Mudas",
        "Estacionamentos", "Galeria de Águas Pluviais", "Jardim", "Mato Alto", "Meio-fio",
        "Parque Infantil", "Passagem Subterrânea", "Passarela", "Pisos Articulados",
        "Pista de Skate", "Poda / Supressão de Árvore", "Ponto de Encontro Comunitário (PEC)",
        "Praça", "Quadra de Esporte", "Rampa", "Rua, Via ou Rodovia (Pista)", "Tapa-buraco",
        "Limpeza de Resíduos da Novacap"
    ]
    for d in sorted(demandas):
        if not Demanda.query.filter_by(descricao=d).first():
            db.session.add(Demanda(descricao=d))

    # 💾 Finaliza a transação
    db.session.commit()
    print("✅ Tabelas criadas (se necessário) e dados essenciais inseridos com sucesso!")
