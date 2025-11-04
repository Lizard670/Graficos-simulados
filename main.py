import mysql
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector
import seaborn as sns
import numpy as np
import os

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class AnalisadorNotasEscolares:
    def __init__(self, fonte_dados, db_config, nome_pasta="gráficos"):
        self.db_config = db_config
        self.conexao = mysql.connector.connect(**db_config)
        cursor = self.conexao.cursor()

        self.pasta_graficos = nome_pasta
        self.categorias_faltas = ['0 faltas', '1 falta', '2 faltas', '3 faltas', '4 faltas']
        self.cores = ['green', 'yellow', 'orange', 'red', 'purple']

        cursor.execute(f"select Nome from Turma")
        self.turmas = [turma[0] for turma in cursor.fetchall()]

        cursor.execute(f"select Nome from Curso")
        self.cursos = [curso[0] for curso in cursor.fetchall()]

        cursor.close()

        if not os.path.exists(self.pasta_graficos):
            os.makedirs(self.pasta_graficos)
        for curso in self.cursos:
            if not os.path.exists(os.path.join(self.pasta_graficos, curso)):
                os.makedirs(os.path.join(self.pasta_graficos, curso))
            for turma in self.turmas:
                if curso not in turma:
                    continue
                if not os.path.exists(os.path.join(self.pasta_graficos, curso, turma)):
                    os.makedirs(os.path.join(self.pasta_graficos, curso, turma))

    def salvar_grafico(self, nome_arquivo):
        caminho = os.path.join(self.pasta_graficos, f"{nome_arquivo}.png")
        plt.savefig(caminho, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Gráfico salvo: {caminho}")

    def estatisticas_basicas(self):
        print(f"\n{"=" * 50}\n{"ESTATÍSTICAS BÁSICAS":^50}\n{"=" * 50}")
        print(self.db_config)
        """

        colunas_analise = ['redacao 1', 'ciencias humanas 1', 'ciencias exatas 1',
                           'redacao 2', 'ciencias humanas 2', 'ciencias exatas 2',
                           'soma', 'soma_periodo_1', 'soma_periodo_2']

        for coluna in colunas_analise:
            print(f"\n{coluna}")
            print(f"  Média: {self.dados_gerais[coluna]['media']:.2f}")
            print(f"  Min: {self.dados_gerais[coluna]['min']:.2f} | Max: {self.dados_gerais[coluna]['max']:.2f}")"""

    def plotar_grafico_multiplo(self, funcao_plot, titulo, nome_arquivo, mostrar, **kwargs):
        """Função auxiliar para plotar gráficos múltiplos"""
        plt.figure(figsize=(12, 8))
        funcao_plot(**kwargs)
        plt.suptitle(titulo)
        plt.tight_layout()
        self.salvar_grafico(nome_arquivo)
        if mostrar:
            plt.show()
        else:
            plt.close()

    def plotar_distribuicao_faltas(self, mostrar):
        def plot():
            cursor = self.conexao.cursor()
            cursor.execute("select count(case when AlunoProva.Nota = 0 and idAssunto != 1 then 1 end) as Faltas,"
                            "	   Turma.Nome as Turma,"
                            "	   Curso.Nome as Curso,"
                            "	   Turma.Ano as Ano"
                            "   from AlunoProva "
                            "	   inner join Prova on AlunoProva.idProva = Prova.idProva"
                            "	   inner join Aluno on AlunoProva.idAluno = Aluno.idAluno"
                            "	   inner join Turma on Aluno.idTurma = Turma.idTurma"
                            "	   inner join Curso on Turma.idCurso = Curso.idCurso"
                            "   group by AlunoProva.idAluno")
            faltas_bruto = cursor.fetchall()

            faltas = {"ano": [[0]*5, [0]*5],
                      "turma": {turma: [0]*5 for turma in self.turmas},
                      "curso": {curso: [0]*5 for curso in self.cursos}}
            quantidade_alunos = {"ano": [[0]*5, [0]*5],
                                 "turma": {turma: [0]*5 for turma in self.turmas},
                                 "curso": {curso: [0]*5 for curso in self.cursos}}

            for aluno in faltas_bruto:
                faltas_aluno = aluno[0]
                turma_aluno = aluno[1]
                curso_aluno = aluno[2]
                ano_aluno = aluno[3]
                faltas["turma"][turma_aluno][faltas_aluno] += 1
                faltas["curso"][curso_aluno][faltas_aluno] += 1
                faltas["ano"][ano_aluno - 3][faltas_aluno] += 1
                quantidade_alunos["turma"][turma_aluno][faltas_aluno] += 1
                quantidade_alunos["curso"][curso_aluno][faltas_aluno] += 1
                quantidade_alunos["ano"][ano_aluno - 3][faltas_aluno] += 1

            faltas["geral"] = []
            quantidade_alunos["geral"] = []
            for i in range(5):
                faltas["geral"].append(faltas["ano"][0][i] + faltas["ano"][1][i])
            grossuraBarra = 0.25

            fig, axes = plt.subplots(2, 2, figsize=(12, 8))
            bars = []
            # Gráfico 1: Distribuição de faltas
            bars.append(axes[0, 0].bar(self.categorias_faltas, faltas["geral"], color=self.cores))
            axes[0, 0].bar_label(bars[0])
            axes[0, 0].set_title('Alunos por Número de Faltas')
            axes[0, 0].set_ylim(0, sum(faltas["geral"]))

            # Gráfico 2: Faltas por ano
            faltas_ano = [[faltas["ano"][0][x],
                           faltas["ano"][1][x]] for x in range(5)]

            brs = [np.arange(len(faltas_ano[1]))]
            for i in range(len(faltas_ano) - 1):
                brs.append(np.array([(x + grossuraBarra) for x in list(brs[i])]))

            bars.append([])
            for i in range(len(self.categorias_faltas)):
                bars[1].append(axes[0, 1].bar(brs[i], faltas_ano[i], color=self.cores[i], width=grossuraBarra,
                                              label=self.categorias_faltas[i]))
                axes[0, 1].bar_label(bars[1][-1])

            axes[0, 1].set_xticks([r + grossuraBarra for r in range(len(faltas_ano[1]))],
                                  ["3°", "4°"])
            axes[0, 1].set_ylim(0, sum(faltas["geral"]))
            axes[0, 1].set_title('Faltas por ano')
            axes[0, 1].tick_params(axis='x')

            # Gráfico 2: Faltas por curso
            faltas_curso = [[faltas["curso"]["TA"][x],
                             faltas["curso"]["TB"][x],
                             faltas["curso"]["TI"][x]] for x in range(5)]

            brs = [np.arange(len(faltas_curso[1]))]
            for i in range(len(faltas_curso) - 1):
                brs.append(np.array([x + grossuraBarra for x in brs[i]]))

            bars.append([])
            for i in range(len(self.categorias_faltas)):
                bars[2].append(axes[1, 0].bar(brs[i], faltas_curso[i], color=self.cores[i], width=grossuraBarra,
                                              label=self.categorias_faltas[i]))
                axes[1, 0].bar_label(bars[2][-1])
            distancias_cursos = []
            for i in range(len(faltas_curso[1])):
                distancias_cursos.append(i + grossuraBarra)
            axes[1, 0].set_xticks(distancias_cursos, self.cursos)
            axes[1, 0].set_ylim(0, sum(faltas["geral"]))
            axes[1, 0].set_title('Faltas por curso')
            axes[1, 0].tick_params(axis='x')

            # Gráfico 3: Média agrupada por faltas
            somas_faltas = [{"quantidade": 0, "soma": 0} for i in range(4)]
            #for aluno in self.dados:
            #    somas_faltas[aluno["faltas"]]["quantidade"] += 1
            #    somas_faltas[aluno["faltas"]]["soma"] += aluno["soma"]

            medias_faltas = []
            try:
                for soma in somas_faltas:
                    medias_faltas.append(soma["soma"] / soma["quantidade"])
            except ZeroDivisionError:
                medias_faltas.append(0)
            bars.append(axes[1, 1].bar(self.categorias_faltas, medias_faltas, color=self.cores))
            axes[1, 1].bar_label(bars[3])
            axes[1, 1].set_ylim(0, 10000)
            axes[1, 1].set_title('Média por faltas')

        self.plotar_grafico_multiplo(plot, 'Análise de faltas', 'distribuicao_faltas', mostrar)

    def plotar_analise_coluna(self, dados, nota_max, coluna, nome, titulo, caminho, mostrar):
        def plot():
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))

            todas = []
            medias = []
            for aluno in dados:
                todas.append(aluno[f"{coluna} 1"])
                todas.append(aluno[f"{coluna} 2"])
                media = (aluno[f"{coluna} 1"] + aluno[f"{coluna} 2"]) / 2
                if aluno[f"{coluna} 1"] == 0 or aluno[f"{coluna} 2"] == 0:
                    media *= 2
                medias.append(media)

            # Distribuição todas as notas
            axes[0, 0].hist(todas, bins=[x * 40 for x in range(nota_max // 40 + 1)], color='lightblue')
            axes[0, 0].set_title('Distribuição de todas as notas')

            # Distribuição média entre as duas notas
            axes[0, 1].hist(medias, bins=[x * 40 for x in range(nota_max // 40 + 1)], color='lightblue')
            axes[0, 1].set_title('Distribuição média entre as duas provas')

            # processa os dados em pontos
            # é uma lista de dicionarios, tendo um dicionario para cada falta
            pontos_diferenca = [{"media": [], "diferenca": [], "quantidades": []} for i in range(2)]
            pontos_soma = [{"media": [], "soma": [], "quantidades": [], "hash": []} for i in range(4)]
            # O gráfico usa area pra decidir o tamanho do ponto, e não raio/diametro
            area_por_aluno = 10
            for aluno in dados:
                # Considera que se o aluno teve nota de 0, ele faltou
                # Um problema disso é que se o estudante zerou a redação fica misturado com que nem fez
                # Para as outras matérias isso é menos relevante já que é improvável que ele tire 0 se ele fez a prova
                faltas = int(aluno[f"{coluna} 1"] == 0) + int(aluno[f"{coluna} 2"] == 0)
                media = (aluno[f"{coluna} 1"] + aluno[f"{coluna} 2"]) / 2
                # Caso o aluno só tenha feito uma das provas, a média não deveria ter sido dividida por 2,
                # então corrigimos isso multiplicando por 2
                if faltas > 0:
                    media *= 2

                # pontos para o gráfico nota do simulado vs média da coluna
                # Um hash meio bruto pra facilitar a procura por notas iguais
                hash_aluno = f"{media}-{aluno["soma"]}"
                # Se já possui um ponto com essa nota, apenas aumenta o tamanho do ponto
                if hash_aluno in pontos_soma[aluno["faltas"]]["hash"]:
                    index = pontos_soma[aluno["faltas"]]["hash"].index(hash_aluno)
                    pontos_soma[aluno["faltas"]]["quantidades"][index] += (area_por_aluno * 2)
                else:
                    # Se não, adiciona um novo ponto
                    pontos_soma[aluno["faltas"]]["media"].append(media)
                    pontos_soma[aluno["faltas"]]["soma"].append(aluno["soma"])
                    pontos_soma[aluno["faltas"]]["quantidades"].append(area_por_aluno * 2)
                    pontos_soma[aluno["faltas"]]["hash"].append(hash_aluno)

                # pontos para o gráfico diferença vs media
                # Se já possui um ponto com essa nota, apenas aumenta o tamanho do ponto
                if media in pontos_diferenca[faltas]["media"]:
                    index = pontos_diferenca[faltas]["media"].index(media)
                    pontos_diferenca[faltas]["quantidades"][index] += area_por_aluno
                else:
                    # Se não, adiciona um novo ponto
                    pontos_diferenca[faltas]["media"].append(media)
                    pontos_diferenca[faltas]["diferenca"].append(aluno[f"{coluna} 2"] - aluno[f"{coluna} 1"])
                    pontos_diferenca[faltas]["quantidades"].append(area_por_aluno)

            # Plota os pontos em nota do simulado vs média da coluna, pulando as categorias sem pontos
            for i in range(4):
                axes[1, 0].scatter(pontos_soma[i]["media"], pontos_soma[i]["soma"],
                                   c=self.cores[i], s=pontos_soma[i]["quantidades"], edgecolors='black', alpha=0.6)
            axes[1, 0].plot([0, nota_max], [0, 10000], "k--", alpha=0.3)
            axes[1, 0].legend(self.categorias_faltas)
            axes[1, 0].set_ylim(0, (max(pontos_soma[0]["soma"]) // 1000 + 1) * 1000)
            axes[1, 0].set_title(f'Comparação nota do simulado vs média das ' + nome)

            # Plota os pontos em diferença vs média, pulando as categorias sem pontos
            legendas = self.categorias_faltas[0:2] + ["Faltou a primeira", "Faltou a segunda"]
            for i in range(2):
                axes[1, 1].scatter(pontos_diferenca[i]["media"], pontos_diferenca[i]["diferenca"],
                                   c=self.cores[i], s=pontos_diferenca[i]["quantidades"], edgecolors='black', alpha=0.8)
            axes[1, 1].plot([-50, nota_max + 50], [-50, nota_max + 50], c='red', alpha=0.1)
            axes[1, 1].plot([-50, nota_max + 50], [50, -nota_max - 50], c='blue', alpha=0.1)
            axes[1, 1].legend(legendas)
            axes[1, 1].plot([-50, nota_max + 50], [0, 0], "k--", alpha=0.3)
            diff_max_pos = (max(max(pontos_diferenca[0]["diferenca"]), max(pontos_diferenca[1]["diferenca"]))
                            + (nota_max / 9))
            diff_max_neg = (min(min(pontos_diferenca[0]["diferenca"]), min(pontos_diferenca[1]["diferenca"]))
                            - (nota_max / 9))
            axes[1, 1].set_ylim(diff_max_neg, diff_max_pos)
            axes[1, 1].set_title(f'Comparação {nome}')

            for i in range(2):
                for j in range(2):
                    axes[i, j].set_xlim(-50, nota_max + 50)

        self.plotar_grafico_multiplo(plot, titulo, caminho, mostrar)

    def plotar_comparacao_colunas(self, mostrar):
        def plot():
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))

            # Scatter período 1 vs período 2
            axes[0, 0].scatter(self.dados['soma_periodo_1'], self.dados['soma_periodo_2'],
                               alpha=0.6, c=self.dados['numero_faltas'], cmap='RdYlGn_r')
            axes[0, 0].plot([0, 300], [0, 300], 'r--', alpha=0.5)
            axes[0, 0].set_xlabel('Soma Período 1')
            axes[0, 0].set_ylabel('Soma Período 2')
            axes[0, 0].set_title('Período 1 vs Período 2')

            # Evolução por turma
            evolucao = self.dados.groupby(['serie', 'turma'])[['soma_periodo_1', 'soma_periodo_2']].mean()
            evolucao['evolucao'] = evolucao['soma_periodo_2'] - evolucao['soma_periodo_1']
            evolucao.reset_index().pivot(index='turma', columns='serie', values='evolucao').plot(
                kind='bar', ax=axes[0, 1])
            axes[0, 1].set_title('Evolução entre Períodos')
            axes[0, 1].tick_params(axis='x', rotation=0)

            # Boxplot períodos
            periodos_data = pd.DataFrame({
                'Período 1': self.dados['soma_periodo_1'],
                'Período 2': self.dados['soma_periodo_2']
            })
            periodos_data.boxplot(ax=axes[1, 0])
            axes[1, 0].set_title('Comparação Períodos')

            # Melhoria por faltas
            self.dados['melhoria'] = self.dados['soma_periodo_2'] - self.dados['soma_periodo_1']
            sns.boxplot(data=self.dados, x='categoria_faltas', y='melhoria',
                        ax=axes[1, 1], palette=['green', 'yellow', 'orange', 'red'])
            axes[1, 1].set_title('Melhoria por Faltas')
            axes[1, 1].axhline(y=0, color='red', linestyle='--', alpha=0.5)

        self.plotar_grafico_multiplo(plot, 'Comparação entre Períodos', 'comparacao_periodos', mostrar)

    def plotar_scatter_analises(self, mostrar):
        def plot():
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))

            # Scatter matrix simplificada
            colunas = ['soma_periodo_1', 'soma_periodo_2', 'soma']
            sns.scatterplot(data=self.dados, x='soma_periodo_1', y='soma_periodo_2',
                            hue='categoria_faltas', ax=axes[0, 0],
                            palette=['green', 'yellow', 'orange', 'red'], alpha=0.6)
            axes[0, 0].plot([0, 300], [0, 300], 'k--', alpha=0.3)
            axes[0, 0].set_title('Período 1 vs Período 2')

            # Testes realizados vs desempenho
            testes_realizados = 6 - self.dados['numero_faltas']
            axes[0, 1].scatter(testes_realizados, self.dados['soma'],
                               alpha=0.6, c=self.dados['numero_faltas'], cmap='RdYlGn_r')
            axes[0, 1].set_xlabel('Testes Realizados')
            axes[0, 1].set_ylabel('Nota Total')
            axes[0, 1].set_title('Desempenho vs Presença')

            # Redação 1 vs 2
            axes[1, 0].scatter(self.dados['redacao 1'], self.dados['redacao 2'],
                               alpha=0.6, c=self.dados['numero_faltas'], cmap='RdYlGn_r')
            axes[1, 0].plot([0, 100], [0, 100], 'k--', alpha=0.3)
            axes[1, 0].set_xlabel('Redação 1')
            axes[1, 0].set_ylabel('Redação 2')
            axes[1, 0].set_title('Redação 1 vs Redação 2')

            # Desempenho por turma
            sns.boxplot(data=self.dados, x='turma', y='soma', hue='serie', ax=axes[1, 1])
            axes[1, 1].set_title('Desempenho por Turma e Série')

        self.plotar_grafico_multiplo(plot, 'Análises de Scatter', 'scatter_analises', mostrar)

    def plotar_correlacao_materias(self, mostrar):
        plt.figure(figsize=(10, 8))
        materias = ['redacao 1', 'ciencias humanas 1', 'ciencias exatas 1',
                    'redacao 2', 'ciencias humanas 2', 'ciencias exatas 2']
        correlacao = self.dados[materias].corr()
        sns.heatmap(correlacao, annot=True, cmap='coolwarm', center=0, fmt='.2f')
        plt.title('Correlação entre Matérias e Períodos')
        self.salvar_grafico('correlacao_materias')
        plt.show()

    def gerar_relatorio_completo(self, mostrar=True):
        print("Gerando análise completa de notas escolares...")
        #print(f"Total de alunos: {len(self.dados)}")

        #self.estatisticas_basicas()

        print("\nGerando visualizações...")
        self.plotar_distribuicao_faltas(mostrar)
        """
        materias = [{"nota_max": 1000, "coluna": "redacao", "nome": "redações"},
                    {"nota_max": 2000, "coluna": "ciencias exatas", "nome": "provas de ciências exatas"},
                    {"nota_max": 2000, "coluna": "ciencias humanas", "nome": "provas de ciências humanas"}]
        
        for materia in materias:
            self.plotar_analise_coluna(self.dados, materia["nota_max"], materia["coluna"], materia["nome"],
                                       f'Análise das provas de {materia["nome"]} de todos os alunos',
                                       f"{materia["nome"]} todos", mostrar)
            for curso in self.dados_gerais["cursos"]:
                self.plotar_analise_coluna([aluno for aluno in self.dados if aluno["curso"] == curso],
                                           materia["nota_max"], materia["coluna"], materia["nome"],
                                           f'Análise das {materia["nome"]} de {curso}',
                                           os.path.join(curso, f"{materia["nome"]}{curso}"), mostrar)
                for turma in self.dados_gerais["turmas"]:
                    if curso not in turma:
                        continue
                    self.plotar_analise_coluna([aluno for aluno in self.dados if aluno["turma"] == turma],
                                               materia["nota_max"], materia["coluna"], materia["nome"],
                                               f'Análise das {materia["nome"]} de {turma}',
                                               os.path.join(curso, turma, f"{materia["nome"]}{turma}"), mostrar)
        self.plotar_scatter_analises(mostrar)
        self.plotar_correlacao_materias(mostrar)
        """
        print(f"\nTodos os gráficos salvos em '{self.pasta_graficos}'")


def main():
    db_config = {
        'host': 'localhost',
        'database': 'Simulados',
        'user': 'root',
        'password': 'toor'
    }
    try:
        analisador = AnalisadorNotasEscolares("notas_u1.csv", db_config)
        analisador.gerar_relatorio_completo(mostrar=True)
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
