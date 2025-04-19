
from app import db
from flask_login import UserMixin
from datetime import datetime

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
    possui_vistoria = db.Column(db.Boolean, default=False)
    oficio_assinado = db.Column(db.Boolean, default=False)
    encerrado_pela_ra = db.Column(db.Boolean, default=False)
    data_encerramento_pela_ra = db.Column(db.Date)

# (demais modelos omitidos aqui para exemplo)
