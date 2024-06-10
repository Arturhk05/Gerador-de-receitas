# Gerador de Receitas

**Link(Ainda em testes):** https://arturhk.pythonanywhere.com/

**Objetivo:** Implementar um sistema web (de temática livre) usando conceitos de orientação de objetos.

## Regras:
- O trabalho é individual. 
- O trabalho deverá ter alguma temática de aplicação. 
- O trabalho deverá ser implementado em Python utilizando o framework Flask. Outros frameworks não serão aceitos! 
- O trabalho deverá ser implementado utiliza a biblioteca SQLAlchemy para a manipulação da base de dados. Outras bibliotecas para manipulação de base dados não serão aceitas! 
- Para o desenvolvimento do trabalho serão aceitos no máximo 3 páginas HTML, no máximo 2 arquivos .py, 1 arquivo .js (opcional) e 1 arquivo .css (opcional)

## Requisitos: 
**O trabalho deverá conter no mínimo:** 

 - [X] Uma funcionalidade para cadastrar dados em uma base de dados.
 - [X] Uma funcionalidade para alterar dados em um base de dados.
 - [X] Uma funcionalidade para excluir dados em um base de dados.
 - [X] Uma página HTML com sessão privada que somente usuários habilitados poderão acessá-la/visualiza-la.
 - [X] Um padrão de projeto criacional.
 - [X] Um padrão de projeto estrutural.
 - [X] Um padrão de projeto comportamental.
 - [X] Uma funcionalidade que utilize a API do ChatGPT.

## Padrões de projeto utilizados

**Padrões de Projeto Criacionais:**
 - Builder - Utilizado para a construção da classe receita.
 - Factory Method - Criar as páginas de erro específicas.

**Padrões de Projeto Estruturais:**
 - Fachada - Utilizado para unificar as funções de salvar dados.

 **Padrões de Projeto Comportamentais:**
 - Template Method - Utilizado para servir de base na construção das páginas de erro.