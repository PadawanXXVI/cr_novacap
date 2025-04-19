from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# O arquivo ext.py é responsável por inicializar as extensões do Flask
# (SQLAlchemy, Migrate, LoginManager) para posterior uso no create_app()
