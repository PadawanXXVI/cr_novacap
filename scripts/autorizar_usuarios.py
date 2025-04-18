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
        print("Usuários pendentes de autorização:\n")
        for usuario in pendentes:
            print(f"ID: {usuario.id_usuario} | Nome: {usuario.nome} | Usuário: {usuario.usuario} | Email: {usuario.email}")
            escolha = input("Aprovar este usuário? (s/n): ").strip().lower()
            if escolha == 's':
                usuario.aprovado = True
                print(f"✅ Usuário {usuario.usuario} aprovado.")
            else:
                print(f"⏭️ Usuário {usuario.usuario} não aprovado.")
        db.session.commit()
        print("\n✔️ Processo de aprovação concluído.")
