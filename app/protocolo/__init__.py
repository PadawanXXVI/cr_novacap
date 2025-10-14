# app/protocolo/__init__.py
"""
Blueprint de Protocolo (atendimentos e interações)
"""
from flask import Blueprint

protocolo_bp = Blueprint('protocolo_bp', __name__)

from app.protocolo import routes  # noqa: E402,F401
