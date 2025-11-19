from dash import Dash, html, dcc, Input, Output  
import plotly.express as px
import dash_ag_grid as dag                       
import dash_bootstrap_components as dbc          
import pandas as pd                              
import mysql.connector

import matplotlib                                
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
import os

plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class GeradorGraficos:
    def __init__(self, db_config, nome_pasta="gráficos"):
        # Conecta com o banco de dados e guarda a conexão para ser utilizada depois
        self.db_config = db_config
        self.conexao = mysql.connector.connect(**db_config)

        # .keys() tem os tipos de faltas e .values() as cores de cada uma
        self.categorias_faltas = {'0 faltas': "#008B13", 
                                  '1 falta':  "#FFFB00", 
                                  '2 faltas': "#FF8800", 
                                  '3 faltas': "#F00000", 
                                  '4 faltas': "#7B00CE"}

        # Puxa do banco de dados o nome das turmas, cursos e assuntos
        cursor = self.conexao.cursor()
        cursor.execute(f"select Nome, idTurma from Turma")
        self.turmas = {turma[1]: turma[0] for turma in cursor.fetchall()}
        cursor.execute(f"select Nome, idCurso from Curso")
        self.cursos = {curso[1]: curso[0] for curso in cursor.fetchall()}
        cursor.execute(f"select Nome, idAssunto from Assunto")
        self.assuntos = {assunto[1]: assunto[0] for assunto in cursor.fetchall()}
        cursor.close()

        # Certifica que as pastas para salvar os gráficos existem
        # Segue a hierarquia de pasta_geral/curso/turma
        self.pasta_graficos = nome_pasta
        if not os.path.exists(self.pasta_graficos):
            os.makedirs(self.pasta_graficos)
        for curso in self.cursos.values():
            if not os.path.exists(os.path.join(self.pasta_graficos, curso)):
                os.makedirs(os.path.join(self.pasta_graficos, curso))
            for turma in self.turmas.values():
                if curso not in turma:
                    continue
                if not os.path.exists(os.path.join(self.pasta_graficos, curso, turma)):
                    os.makedirs(os.path.join(self.pasta_graficos, curso, turma))

        # Cria a frontend do gerador
        self.app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.app.layout = self.gerar_layout()

        # Create interactivity between dropdown component and graph
        @self.app.callback(
            Output('bar-graph-plotly', 'figure'),
            Input('tipo_grafico', 'value'),
            [Input('cursos_filtro', 'value')],
            [Input('anos_filtro', 'value')],
            [Input('turmas_filtro', 'value')],
            Input('tipo_agrupar', 'value'),
        )

        def plot_data(tipo, cursos, anos, turmas, tipo_agrupar):
            fig_bar_plotly = None
            cursos = [] if cursos is None else cursos
            anos = [] if anos is None else anos
            turmas = [] if turmas is None else turmas

            match tipo:
                case "Faltas alunos":      
                    fig_bar_plotly = self.plotar_faltas_alunos(cursos, anos, turmas, tipo_agrupar)
                case "Média":
                    df = pd.read_sql('SELECT idProva, avg(Nota) AS Média FROM AlunoProva GROUP BY idProva', con=self.conexao)

            my_cellStyle = {
                "styleConditions": [
                    {
                        "condition": f"params.colDef.field == '{tipo}'",
                        "style": {"backgroundColor": "#d3d3d3"},
                    },
                    {   "condition": f"params.colDef.field != '{tipo}'",
                        "style": {"color": "black"}
                    },
                ]
            }

            return fig_bar_plotly
        
        self.app.run(debug=False, port=8002)


    def gerar_layout(self):
        tipos_graficos = ["Faltas alunos", "Faltas provas", "Média", "Prova vs Prova", "Simulado vs Simulado"]
        df = pd.read_sql('SELECT idProva, avg(Nota) AS Média FROM AlunoProva GROUP BY idProva', con=self.conexao)
        container = dbc.Container([
            # Título
            html.H1("GRÁFICOS DE DESEMPENHO DOS SIMULADOS", style={'textAlign':'center'}),

            # Dropboxes para seleção do gráfico
            dbc.Row([
                dbc.Col([
                    html.H2("Gráfico", style={'textAlign':'center'}),
                    dcc.Dropdown(
                        id='tipo_grafico',
                        value='Faltas alunos',
                        clearable=False,
                        options=tipos_graficos)
                ], width=4),
    
                dbc.Col([
                    html.H2("Cursos", style={'textAlign':'center'}),
                    dcc.Checklist(
                        id='cursos_filtro',
                        options=self.cursos)
                ], width=1),
    
                dbc.Col([
                    html.H2("Anos", style={'textAlign':'center'}),
                    dcc.Checklist(
                        id='anos_filtro',
                        options=[3, 4])
                ], width=1),
    
                dbc.Col([
                    html.H2("Turmas", style={'textAlign':'center'}),
                    dcc.Checklist(
                        id='turmas_filtro',
                        options=self.turmas)
                ], width=1),
    
                dbc.Col([
                    html.H2("Assuntos", style={'textAlign':'center'}),
                    dcc.Checklist(
                        id='assuntos_filtro',
                        options=self.assuntos)
                ], width=2),
    
                dbc.Col([
                    html.H2("Agrupar por", style={'textAlign':'center'}),
                    dcc.RadioItems(
                        id='tipo_agrupar',
                        value="Curso",
                        options=["Curso", "Ano", "Turma"])
                ], width=2)
            ]),

            dbc.Row([
                dbc.Col([
                    html.Img(id='bar-graph-matplotlib')
                ], width=12)
            ]),

            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='bar-graph-plotly', figure={})
                ], width=12),
            ]),
        ])

        return container


    def salvar_grafico(self, nome_arquivo):
        caminho = os.path.join(self.pasta_graficos, f"{nome_arquivo}.png")
        plt.savefig(caminho, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Gráfico salvo: {caminho}")


    def plotar_faltas_alunos(self, cursos, anos, turmas, agrupar_por):
        """Cria um gráfico de barras que mostra a quantidade de cada tipo de falta"""
        tem_cursos = len(cursos) > 0
        tem_anos = len(anos) > 0
        tem_turmas = len(turmas) > 0
        query = "select Faltas, Curso.Nome as Curso, Turma.Ano as Ano, Turma.Nome as Turma from ProvasAluno "
        # Junções para pegar turma e curso
        query += "inner join Aluno on ProvasAluno.idAluno = Aluno.idAluno "
        query += "inner join Turma on Aluno.idTurma = Turma.idTurma "
        query += "inner join Curso on Turma.idCurso = Curso.idCurso "

        # Adiciona as condições de turma, ano e curso
        if tem_turmas:
            query += f"where Turma.idTurma in ('{'\', \''.join(turmas)}') "
        elif tem_anos:
            query += f"where Turma.Ano in ('{'\', \''.join(anos)}') "
        elif tem_cursos:
            query += f"where Turma.idCurso in ('{'\', \''.join(cursos)}') "
        

        # Executa o query e pega os valores do mysql
        df = pd.read_sql(query, con=self.conexao)
        # Converte o número de faltas e ano em uma string correspondente
        for i, linha_antiga in df.iterrows():
            df['Faltas'] = df["Faltas"].astype(str)
            df.at[i, "Faltas"] = list(self.categorias_faltas.keys())[linha_antiga["Faltas"]]

            df['Ano'] = df["Ano"].astype(str)
            df.at[i, "Ano"] = f"{linha_antiga["Ano"]}º"
        # Pega as cores salvas e corta o final pra que tenha a mesma quantidade de itens que o DF
        cores = list(self.categorias_faltas.values())
        
        # Cria o gráfico de barras das Faltas
        grafico = px.histogram(df, text_auto=True, histfunc="count", 
                               x=agrupar_por, y="Faltas", 
                               color_discrete_sequence=cores, color="Faltas")
        # Muda o eixo Y de "count" para "Quantidade de alunos"
        grafico.update_layout(yaxis_title="Quantidade de alunos")

        return grafico


    def plotar_media(self, cursos, turmas):
        pass


def main():
    db_config = {
        'host': 'localhost',
        'database': 'Simulados',
        'user': 'root',
        'password': 'toor'
    }
    try:
        gerador = GeradorGraficos(db_config)
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
