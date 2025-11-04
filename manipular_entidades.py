import mysql.connector


def ver_tabela(db_config, nome_tabela, nome_colunas=None, conexao=None):
    """Escreve no terminal a tabela formatada.
    Caso os nomes das colunas não sejam passadas, puxa do próprio banco de dados.

    Permite passar uma conexao para melhorar o desempenho."""
    criou_conexao = conexao is None
    if conexao is None:
        conexao = mysql.connector.connect(**db_config)
    cursor = conexao.cursor()

    if nome_colunas is None:
        comando_pegar_nomes = f"""
        SELECT `COLUMN_NAME` 
        FROM `INFORMATION_SCHEMA`.`COLUMNS` 
        WHERE `TABLE_SCHEMA`='{db_config['database']}' 
            AND `TABLE_NAME`='{nome_tabela}';
        """
        cursor.execute(comando_pegar_nomes)
        nome_colunas = cursor.fetchall()

    barra = "=-"*(16 * len(nome_colunas) - 1) + "="
    print(barra + "\n|", end="")
    for nome in nome_colunas:
        print(f"{nome[0]:^30}", end='|')
    print("\n" + barra)

    comando_pegar_entidades = f"select * from {nome_tabela}"
    cursor.execute(comando_pegar_entidades)
    entidades = cursor.fetchall()
    for entidade in entidades:
        for valor in entidade:
            print(f"|{valor:^30}", end="")
        print("|")
    print(barra)

    cursor.close()
    if criou_conexao:
        conexao.close()


def inserir_tabela(db_config, nome_tabela, entidade, conexao=None, commit=True):
    """Insere uma nova entidade na tabela.

    Permite passar uma conexao e desativar o commit para melhorar o desempenho."""
    criou_conexao = conexao is None
    if conexao is None:
        conexao = mysql.connector.connect(**db_config)
    cursor = conexao.cursor()

    colunas = ""
    valores_colunas = ""
    for coluna, valor in entidade.items():
        colunas += coluna + ", "
        valores_colunas += "'" + valor + "', "

    comando_insert = f"use {db_config["database"]}; insert into {nome_tabela} ({colunas[0:-2]}) values ({valores_colunas[0:-2]})"
    try:
        cursor.execute(comando_insert)
        if commit:
            conexao.commit()
    except mysql.connector.errors.IntegrityError as e:
        print(f"{'-' * 100}\n{e}\n{'-' * 100}")

    cursor.close()
    if criou_conexao:
        conexao.close()


def main(db_config=None):
    """Exibe um menu que permite ver e criar entidades para as principais tabelas do banco."""
    if db_config is None:
        db_config = {
            'host': 'localhost',
            'database': 'Simulados',
            'user': 'root',
            'password': 'toor'
        }

    tabelas = ["Curso", "Turma", "Unidade", "Simulado", "Prova"]
    colunas = [["idCurso", "nome"],
               ["idTurma", "nome", "idCurso"],
               ["Numero", "Data_inicio", "Data_fim"],
               ["idSimulado", "Unidade"],
               ["idSimulado", "idProva", "idAssunto", "Data_normal", "Data_segunda_chamada"]]
    menu = f"\n\n{'=-' * 10}="
    for i in range(len(tabelas)):
        menu += f"\n|{i*2+1:>2} - Ver {tabelas[i] + "s":<10}|"
        menu += f"\n|{i*2+2:>2} - Criar {tabelas[i]:<8}|"
    menu += ("\n| 0 - Sair          |"
             f"\n{'=-' * 10}="
             "\n Selecione uma opção: ")
    opcao = -1

    while opcao != 0:
        try:
            opcao = int(input(menu))
            if opcao > 10 or opcao < 0:
                raise ValueError
            if opcao == 0:
                break
        except ValueError:
            print("Opção invalida")
            continue

        index = opcao // 2
        if opcao % 2 == 0:
            entidade = {}
            for coluna in colunas[index]:
                entidade[coluna] = input(coluna + ": ")
            inserir_tabela(db_config, tabelas[index], entidade)
        elif opcao % 2 == 1:
            ver_tabela(db_config, tabelas[index], colunas[index])

        input("\nAperte enter para voltar ao menu")


if __name__ == '__main__':
    main()