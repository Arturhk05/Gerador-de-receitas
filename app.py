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

class ReceitaDB(db.Model):
    __tablename__="receitas"

    id = db.Column(db.Integer, primary_key=True)
    html = db.Column(db.Text)
    criador = db.Column(db.String, primary_key=True)

    def __init__(self, html, nome, criador):
        self.html = html
        self.nome = nome
        self.criador = criador

class Receita(ChatGPT):
    __tablename__="receitas"

    def __init__(self, nome, criador, categoria, dificuldade, observacoes, restricoes):
        super().__init__()
        self.nome = nome
        self.receita = ""
        self.criador = criador
        self.categoria = categoria
        self.dificuldade = dificuldade
        self.observacoes = observacoes
        self.restricoes = restricoes

    def gerarReceita(self):
        receita = self.conexao.chat.completions.create(
            model = self.modelo_inteligencia,
            response_format = self.formato_resposta,
            messages = [
                {"role": "system", "content": "Atue como um chefe de cozinha que gera apenas uma div html de suas receitas"},
                {"role": "user", "content": "Gere uma receita que possua as seguintes informacoes: Categoria: " + self.categoria + " Difuculdade: " + self.dificuldade + " Observacoes: " + self.observacoes + " Restricoes: " + self.restricoes + "Igredientes e modo de preparo."}
            ]
        )
        return receita.choices[0].message.content

class Usuario(db.Model):
    __tablename__="usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, unique=True)
    senha = db.Column(db.String)

    def __init__(self, nome, senha):
        self.nome = nome
        self.senha = senha

    def buscaPorNome(nome):
        user = db.session.query(Usuario).filter_by(nome=nome).first()
        return user

    def cadastrar(nome, senha):
        if nome.replace(" ", "") == "" or senha.replace(" ", "") == "":
            return "Nome ou senha invalidos!"

        verifica = Usuario.buscaPorNome(nome)

        if verifica:
            if verifica.nome == nome:
                return "Este usuário já existe!"

        user = Usuario(nome, senha)
        db.session.add(user)
        db.session.commit()
        return "Usuário criado!"
    
    def logar(nome, senha):
        user = Usuario.buscaPorNome(nome)
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

@app.route("/receitas")
def receitas():
    if 'username' not in session:
        return 'Acesso não autorizado! É preciso logar para gerar uma receita!'

    return render_template('receitas.html')

@app.route("/ingredientes")
def ingredientes():
    if 'username' not in session:
        return 'Acesso não autorizado! É preciso Logar'
    
    nome = format(session['username'])
    user = Usuario.buscaPorNome(nome)

    return render_template('ingredientes.html', user=user)

@app.route("/gerarReceita", methods=['POST', 'GET'])
def gerarReceita():
    if request.method == 'POST':
        categoria = request.form['categoria']
        if categoria == 'outro':
            categoria = request.form['categoriaOutro']

        dificuldade = request.form['dificuldade']
        observacoes = request.form['observacoes']
        restricoes = request.form['restricoes']

        nome = format(session['username'])

        info = Receita("nada", nome, categoria, dificuldade, observacoes, restricoes)

        print(categoria, dificuldade, observacoes, restricoes)
        res = info.gerarReceita()

        return render_template('receitas.html', res=res)
    return redirect(url_for('receitas'))

@app.route('/salvarReceita', methods=['GET', 'POST'])
def salvarReceita():
    if request.method == 'POST':
        res = request.form['res']
        print(res)
        return redirect(url_for('receitas'))
    return render_template('index.html')

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
    return render_template('index.html')

if __name__ == "__main__":
    db.create_all()
    app.run()