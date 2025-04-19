# ext.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Instâncias das extensões Flask
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Este arquivo centraliza a inicialização das extensões.
# Elas serão registradas no app dentro da função create_app() em __init__.py
