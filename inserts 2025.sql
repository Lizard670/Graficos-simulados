use Simulados;

insert into Curso (idCurso, nome) values 
	('1', 'TI'),
	('2', 'TA'),
	('3', 'TB');

insert into Turma (idTurma, nome, idCurso) values 
	('1', '3TIA', '1'),
	('2', '3TIB', '1'),
	('3', '4TI',  '1'),
	('4', '3TA',  '2'),
	('5', '4TA',  '2'),
	('6', '3TB',  '3'),
	('7', '4TB',  '3');

insert into Assunto (idAssunto, Nome, NotaMax) values 
	('1', 'Redação', '1000'),
	('2', 'Linguagens e ciências sociais', '2000'),
	('3', 'Matemática e ciências da natureza', '2000');

insert into Unidade (Numero) values 
	('1'),
	('2'),
	('3');

insert into Simulado (idSimulado, Unidade) values
	('1', '1'),
	('2', '1'),
	('3', '2'),
	('4', '3'),
	('5', '3');

insert into Prova (idSimulado, idProva, idAssunto) values
	('1',  '1', '1'),
	('1',  '2', '2'),
	('1',  '3', '3'),
	('2',  '4', '1'),
	('2',  '5', '2'),
	('2',  '6', '3'),
	('3',  '7', '1'),
	('3',  '8', '2'),
	('3',  '9', '3'),
	('4', '10', '1'),
	('4', '11', '2'),
	('4', '12', '3'),
	('5', '13', '1'),
	('5', '14', '2'),
	('5', '15', '3');
