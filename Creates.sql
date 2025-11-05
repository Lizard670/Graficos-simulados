create database Simulados;
use Simulados;

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
	idAluno int,
	Matricula int,
	Nota int,
	primary key(idProva, Matricula),
	foreign key(idProva) references Prova (idProva),
	foreign key(idAluno) references Aluno (idAluno)
);