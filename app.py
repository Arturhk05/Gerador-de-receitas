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
    __tablename__="ingredientes"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, unique=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    def __init__(self, nome):
        self.nome = nome

class Usuario(db.Model):
    __tablename__="usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, unique=True)
    senha = db.Column(db.String)
    ingredientes = db.relationship('Ingrediente', backref='usuarios')

    def __init__(self, nome, senha):
        self.nome = nome
        self.senha = senha

    def buscaUsuario(nome):
        user = db.session.query(Usuario).filter_by(nome=nome).first()
        return user

    def cadastrar(nome, senha):
        if nome == '' or senha == '' or nome == ' ' or senha == ' ':
            return "Nome ou senha invalidos!"
        
        verifica = Usuario.buscaUsuario(nome)

        if verifica:
            if verifica.nome == nome:
                return "Este usuário já existe!"

        user = Usuario(nome, senha)
        db.session.add(user)
        db.session.commit()
        return "Usuário criado!"
    
    def logar(nome, senha):
        user = Usuario.buscaUsuario(nome)
        if user == None:
            return "Usuario não encontrado!"
        if user.senha != senha:
            return "Senha incorreta!"
        if user.senha == senha:
            session['username'] = user.nome
            return "Logado!"

@app.route("/")
def index():
    users = Usuario.query.all()
    return render_template('index.html', users=users)

@app.route("/cadastro", methods=['POST', 'GET'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']

        return Usuario.cadastrar(nome, senha)
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']

        return Usuario.logar(nome, senha)
    return render_template('login.html')

if __name__ == "__main__":
    db.create_all()
    app.run()