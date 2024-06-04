from flask import Flask, render_template, request, redirect, url_for, session
from openai import OpenAI
from flask_sqlalchemy import SQLAlchemy
from abc import ABC, abstractmethod
import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'minhabase.sqlite3')

app = Flask(__name__)
app.app_context().push()
app.secret_key = "123456"
app.config.from_object(Config)
db = SQLAlchemy(app)

class ChatGPT(ABC):
    chave = ''
    modelo_inteligencia = 'gpt-3.5-turbo-0125'
    formato_resposta = {"type": "text"}
    conexao = None

    def __init__(self):
        self.conexao = OpenAI(api_key = self.chave)

class Ingrediente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, unique=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

    def __init__(self, nome):
        self.nome = nome

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, unique=True)
    senha = db.Column(db.String)
    ingredientes = db.relationship('Ingrediente', backref='usuario')

    def __init__(self, nome, senha):
        self.nome = nome
        self.senha = senha

class PaginaInicial():
    def renderizar():
        return render_template('index.html')

@app.route("/")
def index():
    return PaginaInicial.renderizar()

@app.route("/cadastro", methods=['POST', 'GET'])
def cadastro():
    return "oi"

if __name__ == "__main__":
    db.create_all()
    app.run()