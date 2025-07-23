from flask import Flask, render_template, request
import mysql.connector # importo o mysql connector
# AREA PARA BIBLIOTECAS

app = Flask(__name__)
# AREA DAS FUNÇÕES
@app.route('/', methods=['POST', 'GET'])
def fazer_login():
    if request.method == 'POST':
        conexao = mysql.connector.connect(host='localhost', 
                                  database='chamada_escolar', 
                                  user='root', 
                                  password='JoãoVictor15') #trocar isso dps por uma hash
        if conexao.is_connected():
            print('conetado ao banco de dados!')

        cursor = conexao.cursor()
        matricula = request.form['matricula']
        if len(matricula) == 14:
            cursor.close()
            conexao.close()
            return 'Aluno'
            
            
        else:
            
            nome = 'João Victor de Oliveira Moreira'
            senha = request.form['password']
            sql = 'INSERT INTO chamada_escolar.usuario (matricula, senha, tipo, nome) VALUES (%s, %s, %s, %s)'
            valores = (matricula, senha, 'prof', nome)
            cursor.execute(sql, valores)
            conexao.commit()

            cursor.close()
            conexao.close()
            return 'Professor cadastrado com sucesso!'
        

    return render_template('login.html')

# AREA PARA RODAR
if __name__=='__main__':
    app.run(debug=True)


"""PASSOS PARA ADICIONAR O MYSQL AO PYTHON
    1 - BAIXEI O MYSQL.CONNECTOR E IMPORTEI AO CÓDIGO
    2 - GEREI UMA CONEXÃO COM OS MEUS DADOS E REFERENCIEI O BANCO DE DADOS CHAMADA_ESCOLAR
    3 - POR SEGURANÇA, VERIFICAR SE ESTÁ CONECTADO COM A FUNÇÃO IS_CONNECTED
    4 - CRIO O CURSOR PARA EXECUTAR COMANDOS PELO PYTHON cursor = conexao.cursor()
    é importante fechar a conexão e o cursor no fim da condição"""