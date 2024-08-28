import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

def func(pct, allvals):
    absolute = int(pct / 100.0 * sum(allvals))
    return "{:.0f}%\n({:d})".format(pct, absolute)

try:
    # Conectar ao banco de dados PostgreSQL
    connection = psycopg2.connect(
        user="postgres",
        password="",
        host="localhost",
        port="5432",
        database="baseDeDados"  
    )
    cursor = connection.cursor()
    print("Conexão com o banco de dados estabelecida com sucesso!")

    # Solicitar ao usuário qual gráfico ele deseja ver
    escolha = input("Qual gráfico você deseja ver? (1: Região Onde Mora, 2: Gênero, 3: Ocupação): ")

    if escolha == '1':
        # Análise de Região Onde Mora - Gráfico de Pizza
        query_regiao = """
        SELECT regiao_onde_mora, COUNT(*) AS quantidade
        FROM baseDeDados  
        GROUP BY regiao_onde_mora
        ORDER BY quantidade DESC
        LIMIT 10;  
        """
        df_regiao = pd.read_sql_query(query_regiao, connection)

        # Substituir None por "Não especificado" na coluna de região
        df_regiao['regiao_onde_mora'] = df_regiao['regiao_onde_mora'].fillna('Não especificado')

        # Calcular a porcentagem de cada região
        df_regiao['percentual'] = (df_regiao['quantidade'] / df_regiao['quantidade'].sum()) * 100

        # Exibir os dados de Região Onde Mora
        print("Dados de Região Onde Mora:")
        print(df_regiao)

        plt.figure(figsize=(10, 8))
        colors = plt.get_cmap('tab10').colors  # Definindo as cores

        wedges, texts, autotexts = plt.pie(
            df_regiao['percentual'], 
            labels=None,  # Remover os rótulos diretamente no gráfico
            autopct=lambda pct: func(pct, df_regiao['quantidade']),  # Exibir tanto porcentagem quanto quantidade
            startangle=140, 
            pctdistance=0.85, 
            labeldistance=1.2,
            colors=colors,
            wedgeprops={'edgecolor': 'black'},
            radius=1.2,  # Aumenta o tamanho do gráfico
        )

        # Criar um círculo no meio para transformar o gráfico de pizza em rosca
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        plt.legend(wedges, df_regiao['regiao_onde_mora'], title="Região Onde Mora", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        plt.title('Quantidade e Porcentagem de Registros por Região Onde Mora (Top 10)')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()

    elif escolha == '2':
        # Análise de Gênero - Gráfico de Barras Horizontais
        query_genero = """
        SELECT 
            COALESCE(genero, 'NULL') AS genero, 
            COUNT(*) AS quantidade,
            (COUNT(*) * 100.0 / SUM(COUNT(*)) OVER()) AS percentual
        FROM 
            baseDeDados
        GROUP BY 
            genero
        ORDER BY 
            quantidade DESC;
        """
        df_genero = pd.read_sql_query(query_genero, connection)

        # Exibir os dados de Gênero
        print("Quantidade e porcentagem de registros por gênero:")
        print(df_genero)

        # Gráfico de barras horizontais
        plt.figure(figsize=(10, 8))
        plt.barh(df_genero['genero'], df_genero['quantidade'], color='#66b3ff')
        for index, value in enumerate(df_genero['quantidade']):
            plt.text(value, index, f'{value} ({df_genero["percentual"].iloc[index]:.1f}%)')
        plt.xlabel('Quantidade')
        plt.ylabel('Gênero')
        plt.title('Quantidade e Porcentagem de Registros por Gênero')
        plt.tight_layout()
        plt.show()

    elif escolha == '3':
        # Análise de Ocupação - Gráfico de Barras Horizontais
        query_ocupacao = """
        SELECT ocupacao, COUNT(*) AS quantidade
        FROM baseDeDados  
        GROUP BY ocupacao
        ORDER BY quantidade DESC
        LIMIT 10;  
        """
        df_ocupacao = pd.read_sql_query(query_ocupacao, connection)

        # Substituir None por "Não especificado" na coluna de ocupação
        df_ocupacao['ocupacao'] = df_ocupacao['ocupacao'].fillna('Não especificado')

        # Calcular a porcentagem de cada ocupação
        df_ocupacao['percentual'] = (df_ocupacao['quantidade'] / df_ocupacao['quantidade'].sum()) * 100

        # Exibir os dados de Ocupação
        print("Dados de Ocupação:")
        print(df_ocupacao)

        # Gráfico de barras horizontais
        plt.figure(figsize=(10, 8))
        plt.barh(df_ocupacao['ocupacao'], df_ocupacao['quantidade'], color='#66b3ff')
        for index, value in enumerate(df_ocupacao['quantidade']):
            plt.text(value, index, f'{value} ({df_ocupacao["percentual"].iloc[index]:.1f}%)')
        plt.xlabel('Quantidade')
        plt.ylabel('Ocupação')
        plt.title('Quantidade e Porcentagem de Registros por Ocupação (Top 10)')
        plt.tight_layout()
        plt.show()

    else:
        print("Escolha inválida. Por favor, selecione 1, 2 ou 3.")

except (Exception, psycopg2.Error) as error:
    print("Erro ao conectar ao PostgreSQL:", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("Conexão com o banco de dados encerrada.")
