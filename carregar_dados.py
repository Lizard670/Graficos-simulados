# simple_csv_to_mysql.py - Versão simplificada

import pandas as pd
import mysql.connector


def carregar_alunos(db_config, caminho_arquivo=None, campos=None):
    """Lê o arquivo e adiciona os dados na tabela Aluno"""

    if caminho_arquivo is None:
        caminho_arquivo = input("Digite o caminho para o arquivo: ")

    # Lê o CSV e carrega como Data Frame
    df = pd.read_csv(caminho_arquivo, sep=";")
    print(df)

    # Dicionário que mapeia o nome da coluna para uma tabela/entidade mais exata, normalmente uma prova
    if campos is None:
        campos = {}
        for coluna in df.columns:
            valor = input(f'Nome do campo presente na coluna "{coluna}"(vazio se não quiser salvar): ').strip()
            if valor == '':
                continue

            campos[valor] = list(df.columns).index(coluna)

    if not "Nome" in campos.keys():
        print("O campo de Nome é obrigatório")
        raise ValueError

    if not "Turma" in campos.keys() and not "idTurma" in campos.keys():
        print("O campo de Turma ou idTurma é obrigatório")
        raise ValueError


    # Conecta ao MySQL
    conexao = mysql.connector.connect(**db_config)
    cursor = conexao.cursor()

    turmas = {}
    if not "idTurma" in campos.keys():
        cursor.execute("select * from Turma")
        turmas_bruto = cursor.fetchall()
        for turma in turmas_bruto:
            turmas[turma[2]] = turma[0]

    # Insere dados
    for index, row in df.iterrows():
        # Formata os dados do aluno
        entidade_aluno = {chave: row[valor] for chave, valor in campos.items()}
        if not "idTurma" in campos.keys():
            entidade_aluno["idTurma"] = turmas[row[campos["Turma"]]]
            del entidade_aluno["Turma"]
        entidade_aluno["idTurma"] = str(entidade_aluno["idTurma"])

        # Cria o comando que insere o aluno
        comando = f"insert into Aluno ({', '.join(entidade_aluno.keys())}) values (\"{'\", \"'.join(entidade_aluno.values())}\");\n"
        print(comando, end='')
        # Adiciona todas as provas do aluno
        try:
            cursor.execute(comando)
        except mysql.connector.errors.IntegrityError as e:
            print(f"{'-' * 100}\n{e}\n{'-' * 100}")

    try:
        conexao.commit()
        print(f"{len(df)} Alunos inseridos com sucesso!")
    except Exception as e:
        print(f"Erro: {e}")
        conexao.rollback()
    finally:
        cursor.close()
        conexao.close()


def carregar_aluno_prova(db_config, caminho_arquivo=None, indexes=None):
    """Lê o arquivo e adiciona os dados na tabela ProvaAluno"""
    
    if caminho_arquivo is None:
        caminho_arquivo = input("Digite o caminho para o arquivo: ")

    # Lê o CSV e carrega como Data Frame
    df = pd.read_csv(caminho_arquivo, sep=";")
    print(df)

    # Dicionário que mapeia o nome da coluna para uma tabela/entidade mais exata, normalmente uma prova
    if indexes is None:
        indexes = {"idAluno": -1,
                   "Matricula": -1,
                   "Nome": -1}
        for coluna in df.columns:
            valor = input(f'Id da prova da coluna "{coluna}"(vazio se não for uma prova): ')
            try:
                valor = int(valor)
            except ValueError:
                valor = input(f'Nome da coluna "{coluna}"(Vazio para usar o valor atual): ').strip()
                if valor == '':
                    valor = coluna.strip()

            indexes[valor] = list(df.columns).index(coluna)

    provas = {}
    for chave, index in indexes.items():
        try:
            provas[int(chave)] = index
        except ValueError:
            continue


    if indexes["idAluno"] == -1 and indexes["Matricula"] == -1 and indexes["Nome"] == -1:
        print("Nenhum metodo para encontrar o aluno foi encontrado")
        raise ValueError

    # Conecta ao MySQL
    conexao = mysql.connector.connect(**db_config)
    cursor = conexao.cursor()

    alunos = []
    if indexes["idAluno"] == -1:
        cursor.execute("select * from Aluno")
        alunos = cursor.fetchall()

    # Insere dados
    cont_sucesso = 0
    for index, row in df.iterrows():
        # Pega o id do aluno
        id_aluno = None
        if indexes["idAluno"] != -1:
            id_aluno = row[indexes["idAluno"]]
        else:
            if indexes["Nome"] != -1:
                for aluno in alunos:
                    if aluno[2].lower() == row[indexes["Nome"]].lower():
                        id_aluno = aluno[0]
        if id_aluno is None:
            print(f"Aluno na linha {index} não foi encontrado no banco de dados")
            continue

        # Cria o comando que insere todas as provas
        comando = f"use {db_config["database"]};\n"
        for id_prova, index_prova in provas.items():
            comando += f"insert into AlunoProva (idAluno, idProva, Nota) values ('{id_aluno}', '{id_prova}', '{row[index_prova]}');\n"

        # Adiciona todas as provas do aluno
        try:
            cursor.execute(comando)
            conexao.commit()
        except Exception as e:
            print(f"Erro: {e}")
            conexao.rollback()
            cursor.execute(comando)
        else:
            cont_sucesso += 1

    print(f"{cont_sucesso} registros inseridos com sucesso")
    print(f"falha em inserir {len(df) - cont_sucesso} registro(s)")
    cursor.close()
    conexao.close()


def main():
    db_config = {
        'host': 'localhost',
        'database': 'Simulados',
        'user': 'root',
        'password': 'toor'
    }
    indexes = {
        "idAluno": -1,
        "Matricula": -1,
        "Nome": 0,
        "Turma": 1,
        "1": 2,
        "2": 3,
        "3": 4,
        "4": 5,
        "5": 6,
        "6": 7
    }

    # carregar_alunos(db_config, campos={"Nome": 0, "Turma": 1})
    carregar_aluno_prova(db_config, indexes=indexes)


if __name__ == "__main__":
    main()