from flask import Flask, render_template, request, session
import mysql.connector
import bcrypt

# AREA PARA BIBLIOTECAS

app = Flask(__name__)
app.secret_key = 'os_trombadinhas'

# AREA DAS FUNÇÕES

@app.route('/', methods=['POST', 'GET'])
def fazer_login():
    if request.method == 'POST':
        senha = request.form['login_password']
        matricula = request.form['login_matricula']
        if request.method == 'POST':
            conexao = mysql.connector.connect(
            host='localhost',
            database='chamada_escolar',
            user='root',
            password='JoãoVictor15'  # trocar isso dps por uma hash
            )
        cursor = conexao.cursor()
        sql = "SELECT senha, nome, tipo FROM usuario WHERE matricula = %s"
        cursor.execute(sql, (matricula,))
        resultado = cursor.fetchone()

        if resultado: #se a matricula for encontrada
            senha_hash = resultado[0] #isso aqui pega a primeira consulta
            nome_banco = resultado[1]
            tipo_banco = resultado[2]
            if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')): #isso aq faz a comparação das senhas
                if tipo_banco == 'prof':
                    session['matricula'] = matricula #Tô pegando a matricula do prof pra relacionar ao aluno dps
                    conexao.close()
                    cursor.close()
                    return render_template('cadastrar_aluno.html', nome_banco=nome_banco)
                else:
                    conexao.close()
                    cursor.close()
                    return render_template('home_a.html', nome_banco=nome_banco)
                


            else: #se a senha estiver errada 
                msg = 'Senha incorreta. Tente novamente!'
                conexao.close()
                cursor.close()
                return render_template('login.html', msg=msg)
        else: #se a matricula n for encontrada
            msg = f'A matricula {matricula} não está cadastrada.'
            conexao.close()
            cursor.close()
            return render_template('login.html', msg=msg)
            
    return render_template('login.html')




@app.route('/cadastrar', methods=['POST', 'GET'])
def cadastrar():
    if request.method == 'POST':
        conexao = mysql.connector.connect(
            host='localhost',
            database='chamada_escolar',
            user='root',
            password='JoãoVictor15'  # trocar isso dps por uma hash
        )

        if conexao.is_connected():
            print('Conectado ao banco de dados!')

        cursor = conexao.cursor()
        matricula = request.form['cadastro_matricula']
        nome = request.form['cadastro_nome']
        senha = request.form['cadastro_password']
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

        if len(matricula) == 14:
            sql = 'INSERT INTO chamada_escolar.usuario (nome, matricula, senha, tipo) VALUES (%s, %s, %s, %s)'
            valores = (nome, matricula, senha_hash, 'aluno')
            cursor.execute(sql, valores)
            conexao.commit()
            msg = f'Aluno {nome} cadastrado com sucesso!'

        else:
            if len(matricula) > 6 and len(matricula) < 13:
                msg = f'Matricula inválida!'
                return render_template('cadastrar.html', msg=msg)
            
            sql = 'INSERT INTO chamada_escolar.usuario (nome, matricula, senha, tipo) VALUES (%s, %s, %s, %s)'
            valores = (nome, matricula, senha_hash, 'prof')
            cursor.execute(sql, valores)
            conexao.commit()
            msg = f'Professor {nome} cadastrado com sucesso!'

        cursor.close()
        conexao.close()
        return render_template('cadastrar.html', msg=msg)

    return render_template('cadastrar.html')





@app.route('/cadastrar_aluno', methods=['POST', 'GET'])
def cadastrar_aluno():
     if request.method == 'POST':
        conexao = mysql.connector.connect(
            host='localhost',
            database='chamada_escolar',
            user='root',
            password='JoãoVictor15'  # trocar isso dps por uma hash
        )

        cursor = conexao.cursor()
        nome_aluno = request.form['nome_aluno']
        matricula_aluno = request.form['matricula_aluno']
        tag_aluno = request.form['tag_aluno']
        matricula_professor_responsavel = session.get('matricula')

        sql = 'INSERT INTO chamada_escolar.rfid_tags (chave_tag, nome_aluno, matricula_professor, matricula) VALUES (%s, %s, %s, %s)'
        valores = (tag_aluno, nome_aluno, matricula_professor_responsavel, matricula_aluno)
        cursor.execute(sql, valores)
        conexao.commit()
        msg =  f'Aluno {nome_aluno} adicionado!'
        return render_template('cadastrar_aluno.html', msg=msg)

        


# AREA PARA RODAR
if __name__ == '__main__':
    app.run(debug=True)

"""
PASSOS PARA ADICIONAR O MYSQL AO PYTHON
1 - BAIXEI O MYSQL.CONNECTOR E IMPORTEI AO CÓDIGO
2 - GEREI UMA CONEXÃO COM OS MEUS DADOS E REFERENCIEI O BANCO DE DADOS CHAMADA_ESCOLAR
3 - POR SEGURANÇA, VERIFICAR SE ESTÁ CONECTADO COM A FUNÇÃO IS_CONNECTED
4 - CRIO O CURSOR PARA EXECUTAR COMANDOS PELO PYTHON cursor = conexao.cursor()
É importante fechar a conexão e o cursor no fim da condição
"""