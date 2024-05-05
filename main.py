from flask import Flask, render_template, redirect, request
from flaskext.mysql import MySQL

app = Flask(__name__)
app.config['SECRET_KEY'] = 'PJI1102023;'

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'projeto_escola'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/')
def home(): 
    conn = mysql.connect()
    cursor =conn.cursor()
    cursor.execute("SELECT * from aluno")
    data = cursor.fetchone()
    return render_template('index.html', data = data)

@app.route('/consultar')
def consultar(): 
    return render_template('consultar.html')

@app.route('/aluno')
def aluno(): 
    return render_template('aluno.html')

@app.route('/infos', methods=['POST'])
def infos():
    cpf_ra = request.form.get('cpf_ra')
    print(cpf_ra)
    return redirect('/')

if __name__ in "__main__":
    app.run(debug=True)
