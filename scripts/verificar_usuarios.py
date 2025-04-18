import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.ext import db
from app.models.modelos import Usuario

app = create_app()

with app.app_context():
    pendentes = Usuario.query.filter_by(aprovado=False).all()
    
    if not pendentes:
        print("✅ Nenhum usuário pendente de autorização.")
    else:
        print("Usuários pendentes de autorização:")
        for u in pendentes:
            print(f"- ID: {u.id_usuario}, Nome: {u.nome}, Usuário: {u.usuario}, E-mail: {u.email}")
