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

@app.route('/infos', methods=['POST'])
def infos():
    cpf_ra = request.form.get('cpf_ra')
    print(cpf_ra)
    return redirect('/')

if __name__ in "__main__":
    app.run(debug=True)
