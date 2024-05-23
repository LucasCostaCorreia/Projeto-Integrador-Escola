from flask import Flask, render_template, redirect, request, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'PJI1102023;'

conexao = mysql.connector.connect(
    host="roundhouse.proxy.rlwy.net",       # Endereço do servidor MySQL
    user="root",     # Nome de usuário do MySQL
    password="JoQtogIVbCYqpXsVwvEFmyeimFZlZaXj",   # Senha do MySQL
    database="projeto_escola",  # Nome do banco de dados
    port="22938"
)

# conexao = mysql.connector.connect(
#     host="localhost",    
#     user="root",
#     password="",
#     database="projeto_escola",
# )

if conexao.is_connected():
    print("Conexão bem-sucedida!")

cursor = conexao.cursor()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

admin_hashed_password = generate_password_hash('admin')

class User(UserMixin):
    def __init__(self, id, email, senha):
        self.id = id
        self.email = email
        self.senha = senha

    @staticmethod
    def get(user_id):
        cursor = conexao.cursor(dictionary=True)
        query = "SELECT * FROM professores WHERE id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            return User(user['id'], user['email'], user['senha'])
        return None

    @staticmethod
    def authenticate(email, senha):
        cursor = conexao.cursor(dictionary=True)
        query = "SELECT * FROM professores WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        cursor.close()
        if user and check_password_hash(admin_hashed_password, senha):
            return User(user['id'], user['email'], user['senha'])
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def home(): 
    cursor.execute("SELECT * FROM mensagem")
    data = cursor.fetchall()
    return render_template('index.html', avisos=data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['login']
        senha = request.form['senha']
        user = User.authenticate(email, senha)
        if user:
            login_user(user)
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('painel'))
        else:
            flash('Email ou senha incorretos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout bem-sucedido!', 'success')
    return redirect(url_for('login'))

@app.route('/painel')
@login_required
def painel():
    cursor = conexao.cursor(dictionary=True)
        
    professor_id = current_user.get_id()

    query = """
    SELECT professores.nome, professores.id, materias.materia, materias.id as id_materia
    FROM professores 
    INNER JOIN materias ON materias.professores_id = professores.id 
    WHERE professores.id = %s
    """
    cursor.execute(query, (professor_id,))
    professor = cursor.fetchone()

    query_alunos = """
    SELECT *
    FROM alunos
    """
    cursor.execute(query_alunos,)
    alunos = cursor.fetchall()
    
    if not alunos:
        cursor.close()
        return render_template('painel.html', erro_alunos='Este professor ainda não dá aula!')
    
    cursor.close()
    return render_template('painel.html', professor=professor, alunos=alunos)

@app.route('/consultar')
def consultar(): 
    return render_template('consultar.html')

@app.route('/aluno')
def aluno(): 
    return render_template('aluno.html')

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
        aluno['materias'] = materias
        resultados.append(aluno)

    cursor.close()
    return render_template('aluno.html', alunos=resultados)

@app.route('/notas/<int:aluno_id>', methods=['GET'])
@login_required
def get_notas(aluno_id):
    materias_id = request.args.get('materias_id')
    bimestre = request.args.get('bimestre')
    cursor = conexao.cursor(dictionary=True)
    query = """
    SELECT bimestre, nota, observacao
    FROM alunos_materias
    WHERE alunos_id = %s AND materias_id = %s AND bimestre = %s
    """
    cursor.execute(query, (aluno_id, materias_id, bimestre))
    notas = cursor.fetchall()
    cursor.close()
    return jsonify(notas)

@app.route('/avaliacao', methods=['POST'])
@login_required
def avaliacao():
    aluno_id = request.form.get('aluno_id')
    nota = request.form.get('nota')
    observacao = request.form.get('obs')
    materias_id = request.form.get('materias_id')
    bimestre = request.form.get('bimestre')

    cursor = conexao.cursor()
    try:
        query = """
        INSERT INTO alunos_materias (alunos_id, materias_id, nota, observacao, bimestre)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        nota = VALUES(nota),
        observacao = VALUES(observacao)
        """
        cursor.execute(query, (aluno_id, materias_id, nota, observacao, bimestre))
        conexao.commit()
        return jsonify(message='success')
    except Exception as e:
        conexao.rollback()
        return jsonify(message='error', error=str(e))
    finally:
        cursor.close()


if __name__ in "__main__":
    app.run(debug=True)
