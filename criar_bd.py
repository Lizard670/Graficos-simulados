import mysql.connector


def criar_bd(db_config):
    """Cria o banco de dados se ele ainda não existe"""
    config_sem_db = db_config.copy()
    if "database" in config_sem_db:
        del config_sem_db["database"]

    conexao = mysql.connector.connect(**config_sem_db)
    cursor = conexao.cursor()
    comando = f"create database if not exists {db_config['database']}"
    try:
        cursor.execute(comando)
    finally:
        cursor.close()
        conexao.close()

def criar_tabelas(db_config):
    """Tenta criar as tabelas do banco de dados sem checar se elas já existem"""
    # Conecta ao MySQL
    conexao = mysql.connector.connect(**db_config)
    cursor = conexao.cursor()

    comando = f"use {db_config["database"]};\n" + """
    create table Curso(
        idCurso int primary key not null,
        Nome varchar(40) unique not null
    );
    
    create table Turma (
        idTurma int primary key,
        Ano int, 
        Nome varchar(4) unique,
        idCurso int,
        foreign key(idCurso) references Curso (idCurso)
    );
    
    create table Aluno(
        idAluno int primary key auto_increment,
        Matricula int unique,
        Nome varchar(100),
        Genero char(1),
        idTurma int,
        foreign key(idTurma) references Turma (idTurma)
    );
    
    create table Assunto
    (
        idAssunto int primary key,
        Nome varchar(40),
        NotaMax int
    );
    
    create table Unidade
    (
        Numero int primary key,
        Data_inicio date,
        Data_fim date
    );
    
    create table Simulado
    (
        idSimulado int primary key,
        Unidade int,
        foreign key(Unidade) references Unidade (Numero)
    );
    
    create table Prova
    (
        idProva int primary key,
        idAssunto int,
        idSimulado int,
        Quantidade_questoes int,
        Data_normal date,
        Data_segunda_chamada date,
        foreign key(idAssunto) references Assunto(idAssunto),
        foreign key(idSimulado) references Simulado(idSimulado)
    );
    
    create table AlunoProva(
        idProva int,
        Matricula int,
        Nota int,
        primary key(idProva, Matricula),
        foreign key(idProva) references Prova (idProva),
        foreign key(Matricula) references Aluno (Matricula)
    );
    """

    try:
        cursor.execute(comando)
    finally:
        cursor.close()
        conexao.close()


if __name__ == '__main__':
    config_padrao = {
        'host': 'localhost',
        'database': 'Simulados',
        'user': 'root',
        'password': 'toor'
    }
    criar_bd(config_padrao)
    criar_tabelas(config_padrao)