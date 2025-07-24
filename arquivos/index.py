from flask import Flask, render_template, request
import mysql.connector
import bcrypt
# AREA PARA BIBLIOTECAS

app = Flask(__name__)
# AREA DAS FUNÇÕES

@app.route('/', methods=['POST', 'GET'])
def fazer_login():

    return render_template('login.html')

@app.route('/cadastrar', methods=['POST', 'GET'])
def cadastrar():
   if request.method == 'POST':
        conexao = mysql.connector.connect(host='172.31.240.1', 
                                  database='chamada_escolar', 
                                  user='root', 
                                  password='JoãoVictor15') #trocar isso dps por uma hash
        if conexao.is_connected():
            print('conetado ao banco de dados!')

        cursor = conexao.cursor()
        matricula = request.form['cadastro_matricula']
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        nome = request.form['cadastro_nome']
        senha = request.form['cadastro_password']
        if len(matricula) == 14:
            sql = 'INSERT INTO chamada_escolar.usuario (nome, matricula, senha, tipo) VALUES (%s, %s, %s, %s)'
            valores = (nome, matricula, senha_hash, 'aluno' )
            cursor.execute(sql, valores)
            conexao.commit()
            cursor.close()
            conexao.close()
            msg = f'Aluno {nome} cadastrado com sucesso!'
            return render_template('cadastrar.html', msg=msg)


        else:
            sql = 'INSERT INTO chamada_escolar.usuario (nome, matricula, senha, tipo) VALUES (%s, %s, %s, %s)'
            valores = (nome, matricula, senha_hash, 'prof' )
            cursor.execute(sql, valores)
            conexao.commit()

            cursor.close()
            conexao.close()
            msg = f'Professor {nome} cadastrado com sucesso!'
            return render_template('cadastrar.html', msg=msg)


# AREA PARA RODAR
if __name__=='__main__':
    app.run(debug=True)


"""PASSOS PARA ADICIONAR O MYSQL AO PYTHON
    1 - BAIXEI O MYSQL.CONNECTOR E IMPORTEI AO CÓDIGO
    2 - GEREI UMA CONEXÃO COM OS MEUS DADOS E REFERENCIEI O BANCO DE DADOS CHAMADA_ESCOLAR
    3 - POR SEGURANÇA, VERIFICAR SE ESTÁ CONECTADO COM A FUNÇÃO IS_CONNECTED
    4 - CRIO O CURSOR PARA EXECUTAR COMANDOS PELO PYTHON cursor = conexao.cursor()
    é importante fechar a conexão e o cursor no fim da condição"""