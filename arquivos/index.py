from flask import Flask 
import mysql.connector # importo o mysql connector
# AREA PARA BIBLIOTECAS
conexao = mysql.connector.connect(host='localhost', 
                                  database='chamada_escolar', 
                                  user='root', 
                                  password='JoãoVictor15') #trocar isso dps por uma hash
if conexao.is_connected():
    print('conetado ao banco de dados!')
    cursor = conexao.cursor()

cursor.execute('select * from usuario')
r = cursor.fetchone()
for r in cursor:
    print(r)


cursor.close()
conexao.close()

app = Flask(__name__)
# AREA DAS FUNÇÕES


# AREA PARA RODAR
if __name__=='__main__':
    app.run(debug=True)


"""PASSOS PARA ADICIONAR O MYSQL AO PYTHON
    1 - BAIXEI O MYSQL.CONNECTOR E IMPORTEI AO CÓDIGO
    2 - GEREI UMA CONEXÃO COM OS MEUS DADOS E REFERENCIEI O BANCO DE DADOS CHAMADA_ESCOLAR
    3 - POR SEGURANÇA, VERIFICAR SE ESTÁ CONECTADO COM A FUNÇÃO IS_CONNECTED
    4 - CRIO O CURSOR PARA EXECUTAR COMANDOS PELO PYTHON cursor = conexao.cursor()
    é importante fechar a conexão e o cursor no fim da condição"""