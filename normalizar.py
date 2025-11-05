import pandas as pd


def processar_csv_corrigido(arquivo_entrada, arquivo_saida=None):
    """
    Processa um CSV mantendo as ciências divididas por 2 na soma final
    """

    try:
        # Carregar o arquivo CSV
        df = pd.read_csv(arquivo_entrada)

        print(f"Colunas encontradas: {list(df.columns)}")
        print(f"Valores originais de exemplo:")
        print(df.head())

        # Fazer uma cópia das colunas originais antes de dividir
        # para usar no cálculo da soma
        colunas_ciencias = ['ciencias humanas 1', 'ciencias exatas 1',
                            'ciencias humanas 2', 'ciencias exatas 2']

        # Criar cópias temporárias com os valores originais
        for coluna in colunas_ciencias:
            if coluna in df.columns:
                df[f'{coluna}_original'] = df[coluna]

        # AGORA dividir as colunas de ciências por 2 (apenas para exibição)
        for coluna in colunas_ciencias:
            if coluna in df.columns:
                df[coluna] = df[coluna] / 2
                print(f"✓ {coluna} dividida por 2")

        # Recalcular a soma usando os valores ORIGINAIS das ciências
        # mas dividindo por 2 no cálculo
        df['soma'] = 0

        # Adicionar redações (valores normais)
        if 'redacao 1' in df.columns:
            df['soma'] += df['redacao 1']
        if 'redacao 2' in df.columns:
            df['soma'] += df['redacao 2']

        # Adicionar ciências (valores originais divididos por 2)
        ciencia_pares = [
            ('ciencias humanas 1', 'ciencias humanas 1_original'),
            ('ciencias exatas 1', 'ciencias exatas 1_original'),
            ('ciencias humanas 2', 'ciencias humanas 2_original'),
            ('ciencias exatas 2', 'ciencias exatas 2_original')
        ]

        for coluna_atual, coluna_original in ciencia_pares:
            if coluna_original in df.columns:
                # Usar o valor original dividido por 2
                df['soma'] += df[coluna_original] / 2
                print(f"✓ {coluna_atual} incluída na soma (valor original/2)")

        # Remover as colunas temporárias
        colunas_para_remover = [f'{col}_original' for col in colunas_ciencias
                                if f'{col}_original' in df.columns]
        df.drop(columns=colunas_para_remover, inplace=True)

        # Salvar o novo arquivo
        if arquivo_saida is None:
            arquivo_saida = 'dados_processados_corrigido.csv'

        df.to_csv(arquivo_saida, index=False)
        print(f"\n✅ Arquivo salvo como: {arquivo_saida}")

        # Mostrar resultado
        print(f"\n📊 Valores processados (primeiras linhas):")
        print(df.head())

        return df

    except Exception as e:
        print(f"❌ Erro: {e}")


# Executar a versão corrigida
if __name__ == "__main__":
    processar_csv_corrigido('notas_u1.csv')