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
        sql = "SELECT senha, nome, tipo, carga_horaria, tag_professor FROM usuario WHERE matricula = %s"
        cursor.execute(sql, (matricula,))
        resultado = cursor.fetchone()

        if resultado: #se a matricula for encontrada
            senha_hash = resultado[0] #isso aqui pega a primeira consulta
            nome_banco = resultado[1]
            tipo_banco = resultado[2]
            carga_horaria = resultado[3]
            tag_professor = resultado[4]
            if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')): #isso aq faz a comparação das senhas
                if tipo_banco == 'prof':
                    session['matricula'] = matricula #Tô pegando a matricula do prof pra relacionar ao aluno dps
                    session['carga_horaria'] = carga_horaria
                    if carga_horaria == None and tag_professor == None:
                        return render_template('definir_carga_horaria.html')
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
        carga_horaria = None
        tag_professor = None

        if len(matricula) == 14:
            sql = 'INSERT INTO chamada_escolar.usuario (nome, matricula, senha, tipo, carga_horaria, tag_professor) VALUES (%s, %s, %s, %s, %s, %s)'
            valores = (nome, matricula, senha_hash, 'aluno', carga_horaria, tag_professor)
            cursor.execute(sql, valores)
            conexao.commit()
            msg = f'Aluno {nome} cadastrado com sucesso!'

        else:
            if len(matricula) > 6 and len(matricula) < 13:
                msg = f'Matricula inválida!'
                return render_template('cadastrar.html', msg=msg)
            
            sql = 'INSERT INTO chamada_escolar.usuario (nome, matricula, senha, tipo, carga_horaria, tag_professor) VALUES (%s, %s, %s, %s, %s, %s)'
            valores = (nome, matricula, senha_hash, 'prof',carga_horaria, tag_professor)
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
        presenca_aluno = 0
        matricula_professor_responsavel = session.get('matricula')

        sql = 'INSERT INTO chamada_escolar.alunos (nome, matricula, tag, presenca, matricula_professor) VALUES (%s, %s, %s, %s, %s)'
        valores = (nome_aluno,  matricula_aluno,tag_aluno,presenca_aluno, matricula_professor_responsavel)
        cursor.execute(sql, valores)
        conexao.commit()
        msg =  f'Aluno {nome_aluno} adicionado!'
        cursor.close()
        conexao.close()
        return render_template('cadastrar_aluno.html', msg=msg)


        
@app.route('/carga_horaria', methods=['POST', 'GET'])
def carga_horaria():
    if request.method == 'POST':
        conexao = mysql.connector.connect(
            host='localhost',
            database='chamada_escolar',
            user='root',
            password='JoãoVictor15'  # trocar isso dps por uma hash
        )
        carga_horaria = session.get('carga_horaria')
        tag_professor = request.form['tag_professor']
        cursor = conexao.cursor()
        sql1 = 'UPDATE usuario SET carga_horaria = %s WHERE matricula = %s'
        cursor.execute(sql1, (carga_horaria, session.get('matricula')))

        sql2 = 'UPDATE usuario SET tag_professor = %s WHERE matricula = %s'
        cursor.execute(sql2, (tag_professor, session.get('matricula')))
        
        conexao.commit()
        cursor.close()
        conexao.close()
    
        return render_template('cadastrar_aluno.html')
    return render_template('definir_carga_horaria.html')

@app.route('/listar_alunos', methods=['GET'])
def listar_alunos():
    conexao = mysql.connector.connect(
        host='localhost',
        database='chamada_escolar',
        user='root',
        password='JoãoVictor15'
    )

    cursor = conexao.cursor()
    sql = "SELECT nome, matricula, tag, presenca FROM alunos WHERE matricula_professor = %s"
    cursor.execute(sql, (session.get('matricula'),))
    resultados = cursor.fetchall()

    alunos = []
    carga_horaria = session.get('carga_horaria')

    if carga_horaria is None:
        carga_horaria = 0  # ou algum valor padrão, para evitar erro

    if resultados:
        num_aulas = carga_horaria / 0.75 if carga_horaria else 0

        for nome, matricula, tag, presenca in resultados:
            aulas_vistas = num_aulas - presenca if num_aulas else 0
            percentual = f"{(aulas_vistas / num_aulas) * 100:.2f}%" if num_aulas else "N/A"

            aluno = {
                'nome': nome,
                'matricula': matricula,
                'tag': tag,
                'presenca': presenca,
                'falta':num_aulas-presenca,
                'num_aulas': num_aulas,
                'aulas_vistas': aulas_vistas,
                'percentual': percentual
            }
            alunos.append(aluno)

    cursor.close()
    conexao.close()

    return render_template('listar_alunos.html', alunos=alunos)

@app.route('/editar', methods=['POST'])
def editar():
    conexao = mysql.connector.connect(
        host='localhost',
        database='chamada_escolar',
        user='root',
        password='JoãoVictor15'
    )
    cursor = conexao.cursor()

    matricula = session.get('matricula')
    carga_horaria = session.get('carga_horaria') or 0

    # Buscar presenca do aluno
    sql = "SELECT presenca FROM alunos WHERE matricula = %s"
    cursor.execute(sql, (matricula,))
    resultado = cursor.fetchone()

    if resultado:
        presenca_atual = resultado[0] or 0
        num_aulas = carga_horaria / 0.75 if carga_horaria else 0

        falta_atual = num_aulas - presenca_atual

        try:
            nova_falta = int(request.form['editar'])
        except (ValueError, KeyError):
            nova_falta = 0  # ou trate o erro como preferir

        # Calcular nova presenca
        nova_presenca = num_aulas - (falta_atual - nova_falta)

        # Atualizar presenca no banco
        sql_update = "UPDATE alunos SET presenca = %s WHERE matricula = %s"
        cursor.execute(sql_update, (nova_presenca, matricula))
        conexao.commit()

    cursor.close()
    conexao.close()

    # Redireciona para listar_alunos ou renderiza com mensagem
    return render_template('cadastrar_aluno.html')

    

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