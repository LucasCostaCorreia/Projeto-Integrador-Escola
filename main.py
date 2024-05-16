from flask import Flask, render_template, redirect, request
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'PJI1102023;'

conexao = mysql.connector.connect(
    host="localhost",       # Endereço do servidor MySQL
    user="root",     # Nome de usuário do MySQL
    password="",   # Senha do MySQL
    database="projeto_escola"  # Nome do banco de dados
)

if conexao.is_connected():
    print("Conexão bem-sucedida!")

cursor = conexao.cursor()


@app.route('/')
def home(): 
    cursor.execute("SELECT * FROM alunos")
    data = cursor.fetchall()
    return render_template('index.html', data = data)

@app.route('/consultar')
def consultar(): 
    return render_template('consultar.html')

@app.route('/aluno')
def aluno(): 
    return render_template('aluno.html')

@app.route('/professor')
def professor(): 
    return render_template('professor.html')

@app.route('/painel')
def painel(): 
    return render_template('painel.html')

@app.route('/login', methods=['POST'])
def infos():
    login = request.form.get('login')
    senha = request.form.get('senha')
    if login == 'admin' and senha == 'admin':
        return redirect('/painel')
    else:
        return redirect('/professor')

if __name__ in "__main__":
    app.run(debug=True)
