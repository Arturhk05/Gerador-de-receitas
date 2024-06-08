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

class Receita(ChatGPT):
    def __init__(self, criador, categoria, dificuldade, observacoes, restricoes):
        super().__init__()
        self.criador = criador
        self.categoria = categoria
        self.dificuldade = dificuldade
        self.observacoes = observacoes
        self.restricoes = restricoes
        self.receita = ""

    def editar(self, id):
        receitaAntiga = ReceitaDB.buscaPorId(id)

        receitaAntiga.categoria = self.categoria
        receitaAntiga.dificuldade = self.dificuldade
        receitaAntiga.observacoes = self.observacoes
        receitaAntiga.restricoes = self.restricoes
        receitaAntiga.receita = self.receita

        db.session.commit()

    def deletar(id):
        receita = ReceitaDB.buscaPorId(id)
        db.session.delete(receita)
        db.session.commit()

    def salvar(self):
        receita = ReceitaDB(self.criador, self.categoria, self.dificuldade, self.observacoes, self.restricoes, self.receita)
        db.session.add(receita)
        db.session.commit()
        return "Receita salva"

    def gerarReceita(self):
        receita = self.conexao.chat.completions.create(
            model = self.modelo_inteligencia,
            response_format = self.formato_resposta,
            messages = [
                {"role": "system", "content": "Atue como um chefe de cozinha que gera apenas uma div html de suas receitas"},
                {"role": "user", "content": "Gere uma receita que possua as seguintes especificacoes: Categoria: " + self.categoria + " Difuculdade: " + self.dificuldade + " Observacoes: " + self.observacoes + " Restricoes: " + self.restricoes + "De uma lista APENAS com os ingredientes necessários e o modo de preparaçao."}
            ]
        )
        return receita.choices[0].message.content

    def editarReceita(self):
        receita = self.conexao.chat.completions.create(
            model = self.modelo_inteligencia,
            response_format = self.formato_resposta,
            messages = [
                {"role": "system", "content": "Atue como um chefe de cozinha que gera apenas uma div html de suas receitas"},
                {"role": "user", "content": "Com base na seguinte receita (" + self.receita + ") refaça ela caso as especificaoes estejam diferentes: Categoria: " + self.categoria + " Difuculdade: " + self.dificuldade + " Observacoes: " + self.observacoes + " Restricoes: " + self.restricoes + "De uma lista APENAS com os ingredientes necessários e o modo de preparaçao"}
            ]
        )
        return receita.choices[0].message.content

class ReceitaDB(db.Model):
    __tablename__="receitas"

    id = db.Column(db.Integer, primary_key=True)
    receita = db.Column(db.Text)
    criador = db.Column(db.String)
    categoria = db.Column(db.String)
    dificuldade = db.Column(db.String)
    observacoes = db.Column(db.String)
    restricoes = db.Column(db.String)

    def __init__(self, criador, categoria, dificuldade, observacoes, restricoes, receita):
        self.criador = criador
        self.categoria = categoria
        self.dificuldade = dificuldade
        self.observacoes = observacoes
        self.restricoes = restricoes
        self.receita = receita

    def buscaPorId(id):
        receita = db.session.query(ReceitaDB).filter_by(id=id).first()
        return receita

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

@app.route("/receita")
def receita():
    if 'username' not in session:
        return 'Acesso não autorizado! É preciso logar para gerar uma receita!'

    receita = None

    return render_template('receita.html', receita=receita)

@app.route("/receita/<id>")
def editar(id):
    if 'username' not in session:
        return 'Acesso não autorizado! É preciso logar para editar uma receita!'

    receita = ReceitaDB.buscaPorId(id)

    return render_template('receita.html', receita= receita)

@app.route("/receitasSalvas")
def receitasSalvas():
    receitas = ReceitaDB.query.all()
    receitas.reverse()

    return render_template('receitasSalvas.html', receitas=receitas)

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

        receita = Receita(nome, categoria, dificuldade, observacoes, restricoes)
        receita.receita = receita.gerarReceita()

        print(nome, categoria, dificuldade, observacoes, restricoes)
        print(receita.receita)

        receita.salvar()

        return redirect(url_for('receitasSalvas'))
    return redirect(url_for('receitas'))

@app.route("/editarReceita", methods=['POST', 'GET'])
def editarReceita():
    if request.method == 'POST':
        categoria = request.form['categoria']
        if categoria == 'outro':
            categoria = request.form['categoriaOutro']
        dificuldade = request.form['dificuldade']
        observacoes = request.form['observacoes']
        restricoes = request.form['restricoes']
        receita = request.form['receita']
        id = request.form['id']

        receitaNova = Receita("", categoria, dificuldade, observacoes, restricoes)
        receitaNova.receita = receita
        receitaNova.receita = receitaNova.editarReceita()
        
        receitaNova.editar(id)
        return redirect(url_for('receitasSalvas'))
    return redirect(url_for('receita'))

@app.route('/deletarReceita/<id>', methods=['POST', 'GET'])
def delete(id):
    if 'username' not in session:
        return 'Acesso não autorizado! É preciso logar para deletar uma receita!'

    Receita.deletar(id)
    return redirect(url_for('receitasSalvas'))

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

@app.route('/deslogar')
def deslogar():
    if 'username' not in session:
        return 'Não está logado!'

    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    db.create_all()
    app.run()