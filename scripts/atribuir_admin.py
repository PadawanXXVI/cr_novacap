import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.ext import db
from app.models.modelos import Usuario

app = create_app()

with app.app_context():
    usuarios = Usuario.query.all()

    if not usuarios:
        print("❌ Nenhum usuário encontrado.")
    else:
        print("Usuários disponíveis:
")
        for usuario in usuarios:
            admin_status = "✅ ADMIN" if usuario.is_admin else "—"
            print(f"ID: {usuario.id_usuario} | Nome: {usuario.nome} | Usuário: {usuario.usuario} | {admin_status}")
            escolha = input("Tornar este usuário admin? (s/n): ").strip().lower()
            if escolha == 's':
                usuario.is_admin = True
                print(f"🛡️ Usuário {usuario.usuario} agora é administrador.")
            else:
                print(f"⏭️ Usuário {usuario.usuario} mantido sem privilégios de admin.")
        db.session.commit()
        print("\n✔️ Processo de atribuição de admin concluído.")
