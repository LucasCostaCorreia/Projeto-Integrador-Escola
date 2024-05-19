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
    cursor.execute("SELECT * FROM mensagem")
    data = cursor.fetchall()
    return render_template('index.html', avisos=data)

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
    if login == 'professoramaria@example.com' and senha == 'admin':
        return redirect('/painel')
    else:
        return redirect('/professor')

@app.route('/boletim', methods=['POST'])
def boletim():
    cpf_ra = request.form.get('cpf_ra')

    if not cpf_ra:
        return redirect('/consultar')

    cursor = conexao.cursor(dictionary=True)

    # Primeira query para buscar os alunos
    query = """
    SELECT alunos.id, alunos.nome, alunos.ra, alunos.cpf_responsavel 
    FROM alunos 
    WHERE alunos.ra = %s OR alunos.cpf_responsavel = %s
    """
    cursor.execute(query, (cpf_ra, cpf_ra))
    alunos = cursor.fetchall()

    if not alunos:
        cursor.close()
        return render_template('aluno.html', erro='Nenhum resultado encontrado')

    # Segunda query para buscar as notas para cada aluno
    resultados = []
    for aluno in alunos:
        id = aluno['id']

        query_notas = """
        SELECT alunos_materias.nota, alunos_materias.bimestre, alunos_materias.observacao, materias.materia
        FROM alunos_materias 
        INNER JOIN materias ON alunos_materias.materias_id = materias.id 
        WHERE alunos_materias.alunos_id = %s
        """
        cursor.execute(query_notas, (id,))
        materias = cursor.fetchall()
        print(materias)
        aluno['materias'] = materias
        resultados.append(aluno)

    cursor.close()
    return render_template('aluno.html', alunos=resultados)

if __name__ in "__main__":
    app.run(debug=True)
