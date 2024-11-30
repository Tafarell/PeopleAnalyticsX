# app/__init__.py
from flask import Flask

app = Flask(__name__)

# Configurações do Flask (secret key, etc.)
app.config['SECRET_KEY'] = 'secret-key'

# A linha a seguir vai importar o arquivo de rotas sem causar problemas de circularidade
from app import routes