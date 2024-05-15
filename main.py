from flask import Flask, render_template, redirect, request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'PJI1102023;'

@app.route('/')
def home(): 
    return render_template('index.html')

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
