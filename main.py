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
    email = request.form.get('login')
    senha = request.form.get('senha')
    if email == 'professoramaria@example.com' and senha == 'admin':
        cursor = conexao.cursor(dictionary=True)
        # Primeira query para buscar os professores
        query = """
        SELECT professores.nome, professores.id, materias.materia
        FROM professores 
        INNER JOIN materias ON materias.professores_id = professores.id 
        WHERE professores.email = %s
        """
        cursor.execute(query, (email,))
        professor = cursor.fetchone()
        print(professor)
        
        if not professor:
            cursor.close()
            return render_template('painel.html', erro='Nenhum professor encontrado')

        query_alunos = """
        SELECT materias.materia, alunos.nome as nome_aluno, alunos.id as id_aluno
        FROM materias 
        INNER JOIN alunos_materias ON alunos_materias.materias_id = materias.id 
        INNER JOIN alunos ON alunos.id = alunos_materias.alunos_id 
        WHERE materias.professores_id = %s
        GROUP BY alunos_materias.alunos_id
        """
        cursor.execute(query_alunos, (professor['id'],))
        alunos = cursor.fetchall()

        if not alunos:
            cursor.close()
            return render_template('painel.html', erro_alunos='Este professor ainda não dá aula!')

        print(alunos)
        professor['alunos'] = alunos

        cursor.close()
        return render_template('painel.html', professor=professor)
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
        return render_template('aluno.html', erro='Nenhum aluno encontrado')

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

@app.route('/avaliacao', methods=['POST'])
def avaliacao():
    aluno_id = request.form.get('aluno_id')
    nota = request.form.get('nota')
    obs = request.form.get('obs')


if __name__ in "__main__":
    app.run(debug=True)
