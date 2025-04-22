from app import db
from flask_login import UserMixin
from datetime import datetime

# ----------------------------
# USUÁRIOS DO SISTEMA
# ----------------------------
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

# ----------------------------
# PROCESSOS
# ----------------------------
class Processo(db.Model):
    __tablename__ = 'processos'

    id_processo = db.Column(db.Integer, primary_key=True)
    numero_processo = db.Column(db.String(25), unique=True, nullable=False)
    status_atual = db.Column(db.String(100), nullable=True)
    observacoes = db.Column(db.Text)
    diretoria_destino = db.Column(db.String(100), nullable=False)

    entradas = db.relationship('EntradaProcesso', backref='processo', cascade="all, delete-orphan")

# ----------------------------
# ENTRADAS DE PROCESSO
# ----------------------------
class EntradaProcesso(db.Model):
    __tablename__ = 'entradas_processo'

    id_entrada = db.Column(db.Integer, primary_key=True)
    id_processo = db.Column(db.Integer, db.ForeignKey('processos.id_processo'), nullable=False)
    data_criacao_ra = db.Column(db.Date, nullable=False)
    data_entrada_novacap = db.Column(db.Date, nullable=False)
    data_documento = db.Column(db.Date, nullable=False)
    tramite_inicial = db.Column(db.String(10), nullable=False)
    ra_origem = db.Column(db.String(100), nullable=False)
    id_demanda = db.Column(db.Integer, db.ForeignKey('demandas.id_demanda'), nullable=False)
    id_tipo = db.Column(db.Integer, db.ForeignKey('tipos_demanda.id_tipo'), nullable=False)
    usuario_responsavel = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    responsavel = db.relationship("Usuario", foreign_keys=[usuario_responsavel])
    status_inicial = db.Column(db.String(100), db.ForeignKey('status.descricao'), nullable=False)

    movimentacoes = db.relationship('Movimentacao', backref='entrada', cascade="all, delete-orphan")

# ----------------------------
# MOVIMENTAÇÕES
# ----------------------------
class Movimentacao(db.Model):
    __tablename__ = 'movimentacoes'

    id_movimentacao = db.Column(db.Integer, primary_key=True)
    id_entrada = db.Column(db.Integer, db.ForeignKey('entradas_processo.id_entrada'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    novo_status = db.Column(db.String(100), db.ForeignKey('status.descricao'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    observacao = db.Column(db.Text)

    usuario = db.relationship("Usuario", backref="movimentacoes", lazy=True)

# ----------------------------
# STATUS
# ----------------------------
class Status(db.Model):
    __tablename__ = 'status'

    id_status = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), unique=True, nullable=False)
    ordem_exibicao = db.Column(db.Integer)
    finaliza_processo = db.Column(db.Boolean, default=False)

# ----------------------------
# REGIÕES ADMINISTRATIVAS
# ----------------------------
class RegiaoAdministrativa(db.Model):
    __tablename__ = 'regioes_administrativas'

    id_ra = db.Column(db.Integer, primary_key=True)
    codigo_ra = db.Column(db.String(10), unique=True, nullable=False)
    nome_ra = db.Column(db.String(100), nullable=False)
    descricao_ra = db.Column(db.String(150), nullable=False)

# ----------------------------
# DEMANDAS
# ----------------------------
class Demanda(db.Model):
    __tablename__ = 'demandas'

    id_demanda = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(100), nullable=False)

# ----------------------------
# TIPOS DE DEMANDA
# ----------------------------
class TipoDemanda(db.Model):
    __tablename__ = 'tipos_demanda'

    id_tipo = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(50), nullable=False)

# ----------------------------
# LOGS DE USUÁRIOS
# ----------------------------
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

# ----------------------------
# ALERTAS
# ----------------------------
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

# ----------------------------
# PROTOCOLO DE ATENDIMENTO
# ----------------------------
class ProtocoloAtendimento(db.Model):
    __tablename__ = 'protocolo_atendimento'

    id = db.Column(db.Integer, primary_key=True)
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

    id_usuario_criador = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    interacoes = db.relationship('InteracaoAtendimento', backref='protocolo', cascade="all, delete-orphan")

# ----------------------------
# INTERAÇÕES DE ATENDIMENTO
# ----------------------------
class InteracaoAtendimento(db.Model):
    __tablename__ = 'interacoes_atendimento'

    id = db.Column(db.Integer, primary_key=True)
    id_atendimento = db.Column(db.Integer, db.ForeignKey('protocolo_atendimento.id'), nullable=False)

    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    resposta = db.Column(db.Text, nullable=False)

    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    usuario = db.relationship("Usuario", backref="interacoes_protocolo", lazy=True)
