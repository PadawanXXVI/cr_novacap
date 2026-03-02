# app/models/modelos.py
"""
Modelos do sistema CR-NOVACAP.
Contém entidades de usuários, processos, protocolo, status, demandas, logs e alertas.
Atualizado para incluir a hierarquia Diretoria → Departamento → Demanda (corrigido).
"""

from datetime import datetime
from flask_login import UserMixin
from app.ext import db


# ==========================================================
# 👤 USUÁRIOS DO SISTEMA
# ==========================================================
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.Text, nullable=False)
    aprovado = db.Column(db.Boolean, default=False)
    bloqueado = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    def get_id(self):
        return str(self.id_usuario)


# ==========================================================
# 🧭 DIRETORIAS
# ==========================================================
class Diretoria(db.Model):
    __tablename__ = 'diretorias'

    id_diretoria = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False, unique=True)
    sigla = db.Column(db.String(10))
    descricao_exibicao = db.Column(db.String(120))

    # 🔁 Relação 1:N com Departamentos
    departamentos = db.relationship('Departamento', backref='diretoria', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"<Diretoria {self.sigla or ''} - {self.nome_completo}>"


# ==========================================================
# 🏢 DEPARTAMENTOS
# ==========================================================
class Departamento(db.Model):
    __tablename__ = 'departamentos'

    id_departamento = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    id_diretoria = db.Column(db.Integer, db.ForeignKey('diretorias.id_diretoria'), nullable=False)

    # 🔁 Relação 1:N com Demandas — corrigido para evitar conflito
    demandas = db.relationship('Demanda', back_populates='departamento', cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<Departamento {self.nome}>"


# ==========================================================
# 🧾 DEMANDAS
# ==========================================================
class Demanda(db.Model):
    __tablename__ = 'demandas'

    id_demanda = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)

    # 🔗 Vinculações hierárquicas
    id_diretoria = db.Column(db.Integer, db.ForeignKey('diretorias.id_diretoria'), nullable=True)
    id_departamento = db.Column(db.Integer, db.ForeignKey('departamentos.id_departamento'), nullable=True)

    diretoria = db.relationship("Diretoria", backref="demandas", lazy=True)
    departamento = db.relationship("Departamento", back_populates="demandas", lazy=True)

    def __repr__(self):
        return f"<Demanda {self.descricao}>"


# ==========================================================
# 🧩 TIPOS DE DEMANDA
# ==========================================================
class TipoDemanda(db.Model):
    __tablename__ = 'tipos_demanda'

    id_tipo = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), nullable=False)


# ==========================================================
# 📞 CANAIS DE ATENDIMENTO
# ==========================================================
class CanalAtendimento(db.Model):
    __tablename__ = 'canais_atendimento'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)

    atendimentos = db.relationship('ProtocoloAtendimento', backref='canal', lazy=True)


# ==========================================================
# 🗂️ PROTOCOLO DE ATENDIMENTO (CRM)
# ==========================================================
class ProtocoloAtendimento(db.Model):
    __tablename__ = 'protocolo_atendimento'

    id = db.Column(db.Integer, primary_key=True)
    numero_protocolo = db.Column(db.String(20), unique=True)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

    numero_processo_sei = db.Column(db.String(25))
    numero_requisicao = db.Column(db.Integer)

    nome_solicitante = db.Column(db.String(100), nullable=False)
    tipo_solicitante = db.Column(db.String(30), nullable=False)
    contato_telefone = db.Column(db.String(20))
    contato_email = db.Column(db.String(100))

    ra_origem = db.Column(db.String(100), nullable=False)
    demanda = db.Column(db.String(100), nullable=False)

    assunto = db.Column(db.Text, nullable=False)
    encaminhamento_inicial = db.Column(db.Text, nullable=False)

    id_canal = db.Column(db.Integer, db.ForeignKey('canais_atendimento.id'), nullable=True)
    id_usuario_criador = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    interacoes = db.relationship('InteracaoAtendimento', backref='protocolo', cascade="all, delete-orphan")


# ==========================================================
# 💬 INTERAÇÕES DE ATENDIMENTO
# ==========================================================
class InteracaoAtendimento(db.Model):
    __tablename__ = 'interacoes_atendimento'

    id = db.Column(db.Integer, primary_key=True)
    id_atendimento = db.Column(db.Integer, db.ForeignKey('protocolo_atendimento.id'), nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    resposta = db.Column(db.Text, nullable=False)

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    usuario = db.relationship("Usuario", backref="interacoes_protocolo", lazy=True)


# ==========================================================
# 📑 PROCESSOS
# ==========================================================
class Processo(db.Model):
    __tablename__ = 'processos'

    id_processo = db.Column(db.Integer, primary_key=True)
    numero_processo = db.Column(db.String(25), unique=True, nullable=False)
    status_atual = db.Column(db.String(100))
    observacoes = db.Column(db.Text)
    diretoria_destino = db.Column(db.String(100), nullable=False)

    entradas = db.relationship('EntradaProcesso', backref='processo', cascade="all, delete-orphan")


# ==========================================================
# 🔁 ENTRADAS DE PROCESSO
# ==========================================================
class EntradaProcesso(db.Model):
    __tablename__ = 'entradas_processo'

    id_entrada = db.Column(db.Integer, primary_key=True)
    id_processo = db.Column(db.Integer, db.ForeignKey('processos.id_processo'), nullable=False)
    data_criacao_ra = db.Column(db.Date, nullable=False)
    data_entrada_novacap = db.Column(db.Date, nullable=False)
    data_documento = db.Column(db.Date, nullable=False)
    ra_origem = db.Column(db.String(100), nullable=False)

    id_demanda = db.Column(db.Integer, db.ForeignKey('demandas.id_demanda'), nullable=False)
    usuario_responsavel = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    responsavel = db.relationship("Usuario", foreign_keys=[usuario_responsavel])
    status_inicial = db.Column(db.String(100), db.ForeignKey('status.descricao'), nullable=False)

    movimentacoes = db.relationship('Movimentacao', backref='entrada', cascade="all, delete-orphan")


# ==========================================================
# 🔄 MOVIMENTAÇÕES DE PROCESSOS
# ==========================================================
class Movimentacao(db.Model):
    __tablename__ = 'movimentacoes'

    id_movimentacao = db.Column(db.Integer, primary_key=True)
    id_entrada = db.Column(db.Integer, db.ForeignKey('entradas_processo.id_entrada'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    novo_status = db.Column(db.String(100), db.ForeignKey('status.descricao'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    observacao = db.Column(db.Text)

    usuario = db.relationship("Usuario", backref="movimentacoes", lazy=True)


# ==========================================================
# 🏷️ STATUS
# ==========================================================
class Status(db.Model):
    __tablename__ = 'status'

    id_status = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), unique=True, nullable=False)
    ordem_exibicao = db.Column(db.Integer)
    finaliza_processo = db.Column(db.Boolean, default=False)


# ==========================================================
# 🗺️ REGIÕES ADMINISTRATIVAS
# ==========================================================
class RegiaoAdministrativa(db.Model):
    __tablename__ = 'regioes_administrativas'

    id_ra = db.Column(db.Integer, primary_key=True)
    codigo_ra = db.Column(db.String(10), unique=True, nullable=False)
    nome_ra = db.Column(db.String(100), nullable=False)
    descricao_ra = db.Column(db.String(150), nullable=False)


# ==========================================================
# 📋 LOGS DE USUÁRIOS
# ==========================================================
class LogUsuario(db.Model):
    __tablename__ = 'logs_usuarios'

    id_log = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    acao = db.Column(db.String(100), nullable=False)
    tabela_afetada = db.Column(db.String(100))
    id_referencia = db.Column(db.Integer)
    descricao_detalhada = db.Column(db.Text)
    ip_origem = db.Column(db.String(45))
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)


# ==========================================================
# 🚨 ALERTAS
# ==========================================================
class Alerta(db.Model):
    __tablename__ = 'alertas'

    id_alerta = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    tipo_alerta = db.Column(db.String(100), nullable=False)
    numero_processo = db.Column(db.String(25), nullable=False)
    id_entrada = db.Column(db.Integer, db.ForeignKey('entradas_processo.id_entrada'), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    data_alerta = db.Column(db.DateTime, default=datetime.utcnow)
    respondido = db.Column(db.Boolean, default=False)
    data_resposta = db.Column(db.DateTime)
    forma_resposta = db.Column(db.String(50))