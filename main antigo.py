import sys

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class AnalisadorNotasEscolares:
    def __init__(self, fonte_dados=None):
        self.dados = None
        self.dados_gerais = None
        self.pasta_graficos = "gráficos"

        if not os.path.exists(self.pasta_graficos):
            os.makedirs(self.pasta_graficos)

        if fonte_dados:
            self.carregar_dados(fonte_dados)
        else:
            self.criar_dados_exemplo()

        if self.dados is not None:
            self.processar_dados()

    def carregar_dados(self, fonte):
        try:
            if isinstance(fonte, str) and os.path.exists(fonte):
                self.dados = pd.read_csv(fonte).to_dict("records")
                print(f"Dados carregados de {fonte}")
                print(f"Colunas: {self.dados[0].keys()}")
                return True
            else:
                print(f"Arquivo {fonte} não encontrado. Criando dados de exemplo.")
                self.criar_dados_exemplo()
                return False
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            self.criar_dados_exemplo()
            return False

    def processar_dados(self):
        self.dados_gerais = {}
        colunas = ['redacao 1', 'ciencias humanas 1', 'ciencias exatas 1',
                   'redacao 2', 'ciencias humanas 2', 'ciencias exatas 2']
        self.dados_gerais["total"] = [{"quantidade": 0, "soma": 0}, {"quantidade": 0, "soma": 0},
                                      {"quantidade": 0, "soma": 0}, {"quantidade": 0, "soma": 0}]
        self.dados_gerais['quantidade_faltou_todas'] = 0

        for coluna in colunas:
            self.dados_gerais[coluna] = [{"quantidade": 0, "soma": 0}, {"quantidade": 0, "soma": 0},
                                         {"quantidade": 0, "soma": 0}, {"quantidade": 0, "soma": 0}]

        for i in range(len(self.dados)):
            # Processar faltas
            faltas = (self.dados[i]['ciencias humanas 1'] == 0 + self.dados[i]['ciencias exatas 1'] == 0 +
                      self.dados[i]['ciencias humanas 2'] == 0 + self.dados[i]['ciencias exatas 2'] == 0)
            if faltas > 3:
                self.dados_gerais['quantidade_faltou_todas'] += 1
                self.dados.remove(i)
                continue

            # Calcular as novas somas
            self.dados[i]['soma_periodo_1'] = (self.dados[i]['redacao 1'] +
                                               self.dados[i]['ciencias humanas 1'] + self.dados[i]['ciencias exatas 1'])
            self.dados[i]['soma_periodo_2'] = (self.dados[i]['redacao 2'] +
                                               self.dados[i]['ciencias humanas 2'] + self.dados[i]['ciencias exatas 2'])
            for coluna in colunas:
                self.dados_gerais[coluna][faltas]["soma"] += self.dados[i][coluna]
                self.dados_gerais[coluna][faltas]["quantidade"] += 1

        for i in range(4):
            for j in range(1, 3):
                f = str(j)
                self.dados_gerais['periodo_' + f] = [{}, {}, {}, {}]
                self.dados_gerais['periodo_'+f][i]["soma"] = \
                    (self.dados_gerais['redacao '+f][i]["soma"] +
                     self.dados_gerais['ciencias humanas '+f][i]["soma"] +
                     self.dados_gerais['ciencias exatas '+f][i]["soma"])

                self.dados_gerais['periodo_'+f][i]["quantidade"] = \
                    (self.dados_gerais['redacao '+f][i]["quantidade"] +
                     self.dados_gerais['ciencias humanas '+f][i]["quantidade"] +
                     self.dados_gerais['ciencias exatas '+f][i]["quantidade"])

                if self.dados_gerais["periodo_"+f][i]["quantidade"] == 0:
                    self.dados_gerais["periodo_" + f][i]["media"] = 0
                else:
                    self.dados_gerais["periodo_"+f][i]["media"] = (self.dados_gerais["periodo_"+f][i]["soma"] /
                                                                   self.dados_gerais["periodo_"+f][i]["quantidade"])

            self.dados_gerais["total"][i]["soma"] = (self.dados_gerais['periodo_1'][i]["soma"] +
                                                     self.dados_gerais['periodo_2'][i]["soma"])
            self.dados_gerais["total"][i]["quantidade"] = (self.dados_gerais['periodo_1'][i]["quantidade"] +
                                                           self.dados_gerais['periodo_2'][i]["quantidade"])
            if self.dados_gerais["total"][i]["quantidade"] == 0:
                self.dados_gerais["total"][i]["media"] = 0
            else:
                self.dados_gerais["total"][i]["media"] = (self.dados_gerais["total"][i]["soma"] /
                                                          self.dados_gerais["total"][i]["quantidade"])

        print(f"\nAnálise de faltas:")
        print(self.dados_gerais)
        for i in range(4):
            print(f" Alunos com {i} faltas: {self.dados_gerais["total"][i]["quantidade"]}")

    def criar_dados_exemplo(self):
        np.random.seed(42)
        series = ['1º Ano EM', '2º Ano EM']
        turmas = ['A', 'B', 'C', 'D']

        dados = []
        for serie in series:
            for turma in turmas:
                for _ in range(20):
                    aluno = {'serie': serie, 'turma': turma}
                    nota_base = 75 if serie == '1º Ano EM' else 80
                    prob_falta = 0.12 if serie == '1º Ano EM' else 0.08
                    prob_zero_redacao = 0.08 if serie == '1º Ano EM' else 0.05

                    # Gerar notas
                    materias = ['redacao 1', 'ciencias humanas 1', 'ciencias exatas 1',
                                'redacao 2', 'ciencias humanas 2', 'ciencias exatas 2']
                    notas = []

                    for i, materia in enumerate(materias):
                        nota = np.random.normal(nota_base, 12 if 'redacao' in materia else
                        10 if 'humanas' in materia else 15)
                        nota = max(0, min(100, nota))

                        # Aplicar faltas e zeros de redação
                        if 'redacao' in materia:
                            if np.random.random() < prob_zero_redacao:
                                nota = 0
                        else:
                            if np.random.random() < prob_falta:
                                nota = 0

                        aluno[materia] = round(nota, 1)
                        notas.append(nota)

                    aluno['soma'] = round(sum(notas), 1)
                    dados.append(aluno)

        self.dados = pd.DataFrame(dados).to_dict("records")
        print("Dados de exemplo criados!")

    def salvar_grafico(self, nome_arquivo):
        caminho = os.path.join(self.pasta_graficos, f"{nome_arquivo}.png")
        plt.savefig(caminho, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Gráfico salvo: {caminho}")

    def estatisticas_basicas(self):
        print("\n" + "=" * 50)
        print("ESTATÍSTICAS BÁSICAS")
        print("=" * 50)

        colunas_analise = ['redacao 1', 'ciencias humanas 1', 'ciencias exatas 1',
                           'redacao 2', 'ciencias humanas 2', 'ciencias exatas 2',
                           'soma', 'soma_periodo_1', 'soma_periodo_2']

        for coluna in colunas_analise:
            if coluna in self.dados.columns:
                dados_coluna = self.dados[coluna] if coluna.startswith('redacao') else self.dados[coluna][
                    self.dados[coluna] > 0]
                if len(dados_coluna) > 0:
                    print(f"\n{coluna}:")
                    print(f"  Média: {dados_coluna.mean():.2f} | Mediana: {dados_coluna.median():.2f}")
                    print(f"  Min: {dados_coluna.min():.2f} | Max: {dados_coluna.max():.2f}")

    def plotar_grafico_multiplo(self, funcao_plot, titulo, nome_arquivo, **kwargs):
        """Função auxiliar para plotar gráficos múltiplos"""
        plt.figure(figsize=(12, 8))
        funcao_plot(**kwargs)
        plt.suptitle(titulo)
        plt.tight_layout()
        self.salvar_grafico(nome_arquivo)
        plt.show()

    def plotar_distribuicao_faltas(self):
        def plot():
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))

            # Gráfico 1: Distribuição de faltas
            categorias_faltas = ['0 faltas', '1 falta', '2 faltas', '3+ faltas']
            contagens = [x["quantidade"] for x in self.dados_gerais["total"]]
            cores = ['green', 'yellow', 'orange', 'red']
            axes[0, 0].bar(categorias_faltas, contagens, color=cores, alpha=0.7)
            axes[0, 0].set_title('Alunos por Número de Faltas')

            # Gráfico 2: Faltas por ano
            pd.crosstab(self.dados['serie'], self.dados['categoria_faltas']).plot(
                kind='bar', ax=axes[0, 1], color=cores)
            axes[0, 1].set_title('Faltas por ano')
            axes[0, 1].tick_params(axis='x')

            # Gráfico 3: Média por faltas
            medias = [x["media"] for x in self.dados_gerais["total"]]
            axes[1, 0].bar(categorias_faltas, medias, color=cores, alpha=0.7)
            axes[1, 0].set_title('Média por Faltas')

            # Gráfico 4: Matérias mais faltadas
            colunas_nao_redacao = ['ciencias humanas 1', 'ciencias exatas 1',
                                   'ciencias humanas 2', 'ciencias exatas 2']
            faltas_materias = {coluna: 0 for coluna in colunas_nao_redacao}
            for coluna in colunas_nao_redacao:
                for i in range(4):
                    faltas_materias += self.dados_gerais["total"][i]["quantidade"] * i

            axes[1, 1].bar(colunas_nao_redacao, faltas_materias, color='lightblue', alpha=0.7)
            axes[1, 1].set_title('Faltas por Matéria')
            axes[1, 1].tick_params(axis='x', rotation=45)

            for ax in axes.flat:
                for bar in ax.containers:
                    ax.bar_label(bar, fmt='%d')

        self.plotar_grafico_multiplo(plot, 'Análise de Faltas', 'distribuicao_faltas')

    def plotar_analise_redacao(self):
        def plot():
            fig, axes = plt.subplots(2, 2, figsize=(12, 8))

            # Distribuição redações
            axes[0, 0].hist(self.dados['redacao 1'], bins=20, alpha=0.7, label='Redação 1', color='lightblue')
            axes[0, 0].hist(self.dados['redacao 2'], bins=20, alpha=0.7, label='Redação 2', color='lightcoral')
            axes[0, 0].set_title('Distribuição Redações')
            axes[0, 0].legend()

            # Zeros por redação
            zeros = [('Redação 1', (self.dados['redacao 1'] == 0).sum()),
                     ('Redação 2', (self.dados['redacao 2'] == 0).sum())]
            nomes, contagens = zip(*zeros)
            axes[0, 1].bar(nomes, contagens, color=['lightblue', 'lightcoral'], alpha=0.7)
            axes[0, 1].set_title('Zeros em Redação')

            # Zeros vs Faltas
            pd.crosstab(self.dados['categoria_faltas'],
                        (self.dados['redacao 1'] == 0) | (self.dados['redacao 2'] == 0)).plot(
                kind='bar', ax=axes[1, 0], color=['lightblue', 'orange'])
            axes[1, 0].set_title('Zeros Redação vs Faltas')
            axes[1, 0].tick_params(axis='x', rotation=45)

            # Média com/sem zeros
            tem_zeros = (self.dados['redacao 1'] == 0) | (self.dados['redacao 2'] == 0)
            medias = [self.dados[tem_zeros]['soma'].mean(),
                      self.dados[~tem_zeros]['soma'].mean()]
            axes[1, 1].bar(['Com Zeros', 'Sem Zeros'], medias, color=['orange', 'lightblue'], alpha=0.7)
            axes[1, 1].set_title('Média com/sem Zeros Redação')

            for ax in axes.flat:
                for bar in ax.containers:
                    ax.bar_label(bar, fmt='%.1f' if ax == axes[1, 1] else '%d')

        self.plotar_grafico_multiplo(plot, 'Análise de Redação', 'analise_redacao')

    def plotar_comparacao_periodos(self):
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

        self.plotar_grafico_multiplo(plot, 'Comparação entre Períodos', 'comparacao_periodos')

    def plotar_scatter_analises(self):
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

        self.plotar_grafico_multiplo(plot, 'Análises de Scatter', 'scatter_analises')

    def plotar_correlacao_materias(self):
        plt.figure(figsize=(10, 8))
        materias = ['redacao 1', 'ciencias humanas 1', 'ciencias exatas 1',
                    'redacao 2', 'ciencias humanas 2', 'ciencias exatas 2']
        correlacao = self.dados[materias].corr()
        sns.heatmap(correlacao, annot=True, cmap='coolwarm', center=0, fmt='.2f')
        plt.title('Correlação entre Matérias e Períodos')
        self.salvar_grafico('correlacao_materias')
        plt.show()

    def gerar_relatorio_completo(self):
        print("Gerando análise completa de notas escolares...")
        print(f"Total de alunos: {len(self.dados)}")

        self.estatisticas_basicas()

        print("\nGerando visualizações...")
        self.plotar_distribuicao_faltas()
        self.plotar_analise_redacao()
        self.plotar_comparacao_periodos()
        self.plotar_scatter_analises()
        self.plotar_correlacao_materias()

        print(f"\nTodos os gráficos salvos em '{self.pasta_graficos}'")


def main():
    try:
        analisador = AnalisadorNotasEscolares("notas_u1.csv")
        #analisador.salvar_dados_exemplo('notas_exemplo.csv')
        analisador.gerar_relatorio_completo()
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
