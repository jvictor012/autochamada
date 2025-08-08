from flask import Flask, render_template, request, session
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = 'os_trombadinhas'

@app.route('/cadastrar', methods=['POST', 'GET'])
def cadastrar():
    if request.method == 'POST':
        conexao = None
        cursor = None
        try:
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
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            carga_horaria = None
            tag_professor = None

            if len(matricula) == 14:
                sql_a = 'SELECT matricula FROM usuario WHERE matricula = %s'
                cursor.execute(sql_a, (matricula,))
                resultado = cursor.fetchone()
                if resultado and resultado[0] == matricula:
                    msg = f'Impossível cadastrar a matricula {matricula} pois ela já está em uso!'
                    return render_template('cadastrar.html', msg=msg)

                sql = 'INSERT INTO chamada_escolar.usuario (nome, matricula, senha, tipo, carga_horaria, tag_professor) VALUES (%s, %s, %s, %s, %s, %s)'
                valores = (nome, matricula, senha_hash, 'aluno', carga_horaria, tag_professor)
                cursor.execute(sql, valores)
                conexao.commit()
                msg = f'Aluno {nome} cadastrado com sucesso!'

            else:
                if 6 < len(matricula) < 13:
                    msg = f'Matricula inválida!'
                    return render_template('cadastrar.html', msg=msg)

                sql_a = 'SELECT matricula FROM usuario WHERE matricula = %s'
                cursor.execute(sql_a, (matricula,))
                resultado = cursor.fetchone()
                if resultado and resultado[0] == matricula:
                    msg = f'Impossível cadastrar a matricula {matricula} pois ela já está em uso!'
                    return render_template('cadastrar.html', msg=msg)
                
                sql = 'INSERT INTO chamada_escolar.usuario (nome, matricula, senha, tipo, carga_horaria, tag_professor) VALUES (%s, %s, %s, %s, %s, %s)'
                valores = (nome, matricula, senha_hash, 'prof', carga_horaria, tag_professor)
                cursor.execute(sql, valores)
                conexao.commit()
                msg = f'Professor {nome} cadastrado com sucesso!'

        finally:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()

        return render_template('cadastrar.html', msg=msg)

    return render_template('cadastrar.html')


@app.route('/', methods=['POST', 'GET'])
def fazer_login():
    if request.method == 'POST':
        conexao = None
        cursor = None
        try:
            conexao = mysql.connector.connect(
                host='localhost',
                database='chamada_escolar',
                user='root',
                password='JoãoVictor15'  # trocar isso dps por uma hash
            )
            cursor = conexao.cursor()
            matricula = request.form['login_matricula']
            senha = request.form['login_password']

            sql = "SELECT senha, nome, tipo, carga_horaria, tag_professor FROM usuario WHERE matricula = %s"
            cursor.execute(sql, (matricula,))
            resultado = cursor.fetchone()

            if resultado:  # se a matricula for encontrada
                senha_hash = resultado[0]
                nome_banco = resultado[1]
                tipo_banco = resultado[2]
                carga_horaria = resultado[3]
                tag_professor = resultado[4]
                if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
                    if tipo_banco == 'prof':
                        session['matricula'] = matricula
                        session['carga_horaria'] = carga_horaria
                        if carga_horaria is None and tag_professor is None:
                            return render_template('definir_carga_horaria.html')
                        return render_template('home_p.html', nome_banco=nome_banco)
                    else:
                        return render_template('home_a.html', nome_banco=nome_banco)
                else:
                    msg = 'Senha incorreta. Tente novamente!'
                    return render_template('login.html', msg=msg)
            else:
                msg = f'A matricula {matricula} não está cadastrada.'
                return render_template('login.html', msg=msg)

        finally:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()

    return render_template('login.html')


@app.route('/cadastrar_aluno', methods=['POST', 'GET'])
def cadastrar_aluno():
    if request.method == 'POST':
        conexao = None
        cursor = None
        try:
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
            valores = (nome_aluno, matricula_aluno, tag_aluno, presenca_aluno, matricula_professor_responsavel)
            cursor.execute(sql, valores)
            conexao.commit()
            msg = f'Aluno {nome_aluno} adicionado!'

        finally:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()

        return render_template('cadastrar_aluno.html', msg=msg)

    return render_template('cadastrar_aluno.html')


@app.route('/carga_horaria', methods=['POST', 'GET'])
def carga_horaria():
    if request.method == 'POST':
        conexao = None
        cursor = None
        try:
            conexao = mysql.connector.connect(
                host='localhost',
                database='chamada_escolar',
                user='root',
                password='JoãoVictor15'  # trocar isso depois por uma hash segura
            )
            cursor = conexao.cursor()

            # Converte a carga horária recebida para float (evita erros em cálculos)
            carga_horaria = float(request.form.get('carga_horaria') or session.get('carga_horaria') or 0)
            tag_professor = request.form['tag_professor']

            # Atualiza os dados no banco
            sql1 = 'UPDATE usuario SET carga_horaria = %s WHERE matricula = %s'
            cursor.execute(sql1, (carga_horaria, session.get('matricula')))

            sql2 = 'UPDATE usuario SET tag_professor = %s WHERE matricula = %s'
            cursor.execute(sql2, (tag_professor, session.get('matricula')))

            conexao.commit()

            # Atualiza os dados na sessão
            session['carga_horaria'] = carga_horaria
            session['tag_professor'] = tag_professor

        finally:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()

        return render_template('cadastrar_aluno.html')

    return render_template('definir_carga_horaria.html')



@app.route('/listar_alunos', methods=['GET'])
def listar_alunos():
    conexao = None
    cursor = None
    try:
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
        print(carga_horaria)

        if carga_horaria is None:
            carga_horaria = 0

        if resultados:
            num_aulas = carga_horaria / 0.75 if carga_horaria else 0
            print(num_aulas)
            print(carga_horaria)

            for nome, matricula, tag, presenca in resultados:
                percentual = f"{(presenca / num_aulas) * 100:.2f}%" if num_aulas else "N/A"

                aluno = {
                    'nome': nome,
                    'matricula': matricula,
                    'tag': tag,
                    'presenca': presenca,
                    'falta': num_aulas - presenca,
                    'total_de_aulas':num_aulas,
                    'num_aulas': num_aulas,
                    'percentual': percentual
                }
                alunos.append(aluno)

        return render_template('listar_alunos.html', alunos=alunos)

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@app.route('/editar', methods=['POST'])
def editar():
    conexao = None
    cursor = None
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            database='chamada_escolar',
            user='root',
            password='JoãoVictor15'
        )
        cursor = conexao.cursor()

        matricula = request.form.get('matricula_aluno') or session.get('matricula')
        carga_horaria = int(session.get('carga_horaria') or 0)

        sql = "SELECT presenca FROM alunos WHERE matricula = %s"
        cursor.execute(sql, (matricula,))
        resultado = cursor.fetchone()

        if resultado:
            presenca_atual = resultado[0] or 0
            num_aulas = float(carga_horaria) / 0.75 if carga_horaria else 0

            falta_atual = num_aulas - presenca_atual

            try:
                nova_falta = int(request.form['editar'])
            except (ValueError, KeyError):
                nova_falta = 0

            nova_presenca = num_aulas - (falta_atual - nova_falta)

            sql_update = "UPDATE alunos SET presenca = %s WHERE matricula = %s"
            cursor.execute(sql_update, (nova_presenca, matricula))
            conexao.commit()

        return render_template('cadastrar_aluno.html')

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


@app.route('/justificar_falta', methods=['GET', 'POST'])
def justificar_falta():
    if request.method == 'POST':
        conexao = None
        cursor = None
        try:
            conexao = mysql.connector.connect(
                host='localhost',
                database='chamada_escolar',
                user='root',
                password='JoãoVictor15'
            )
            cursor = conexao.cursor()
            matricula = request.form['matricula']
            matricula_professor = request.form['matricula_p']
            justificativa = request.form['justificar_falta']

            sql = "SELECT tipo, matricula, nome FROM usuario WHERE matricula = %s"
            cursor.execute(sql, (matricula_professor,))
            resultado = cursor.fetchone()
            cursor.fetchall()  # limpa resultado

            if resultado:
                tipo_usuario, _, nome_professor = resultado
                if tipo_usuario == 'prof':
                    sql = "SELECT nome FROM alunos WHERE matricula = %s"
                    cursor.execute(sql, (matricula,))
                    resultado_aluno = cursor.fetchone()
                    cursor.fetchall()  # limpa resultado

                    if resultado_aluno:
                        nome_aluno = resultado_aluno[0]

                        sql = '''
                            INSERT INTO chamada_escolar.notificacoes 
                            (aluno, matricula_aluno, justificativa, matricula_professor_destinado) 
                            VALUES (%s, %s, %s, %s)
                        '''
                        valores = (nome_aluno, matricula, justificativa, matricula_professor)
                        cursor.execute(sql, valores)
                        conexao.commit()

                        msg = f'Justificativa de falta enviada para o professor {nome_professor}'
                        return render_template('home_a.html', msg=msg)
                    else:
                        msg = 'Aluno não encontrado! Verifique a matrícula.'
                        return render_template('home_a.html', msg=msg)
            else:
                msg = 'Erro! Verifique os campos novamente!'
                return render_template('home_a.html', msg=msg)

        finally:
            if cursor:
                cursor.close()
            if conexao and conexao.is_connected():
                conexao.close()

    msg = 'Erro inesperado!'
    return render_template('home_a.html', msg=msg)

@app.route('/homepage', methods=['GET', 'POST'])
def home_professor():
    return render_template('home_p.html')


@app.route('/mostrar_notificacoes', methods=['GET', 'POST'])
def mostrar_notificacoes():
    notificacoes = []
    conexao = None
    cursor = None
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            database='chamada_escolar',
            user='root',
            password='JoãoVictor15'
        )
        cursor = conexao.cursor()

        sql = 'SELECT aluno, matricula_aluno, justificativa, matricula_professor_destinado FROM notificacoes WHERE matricula_professor_destinado = %s'
        cursor.execute(sql, (session.get('matricula'),))
        resultado = cursor.fetchall()

        if resultado:
            for aluno, matricula_aluno, justificativa, matricula_professor_destinado in resultado:
                notificacao = {
                    'aluno': aluno,
                    'matricula_aluno': matricula_aluno,
                    'justificativa': justificativa,
                    'matricula_professor_destinado': matricula_professor_destinado
                }
                notificacoes.append(notificacao)

        return render_template('mostrar_notificacoes.html', notificacoes=notificacoes)

    finally:
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()


if __name__ == '__main__':
    app.run(debug=True)
