from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
# O arquivo ext.py é responsável por inicializar as extensões do Flask que serão utilizadas na aplicação.