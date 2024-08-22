import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

def func(pct, allvals):
    absolute = int(pct / 100.0 * sum(allvals))
    return "{:.0f}%".format(pct)

try:
    # Conectar ao banco de dados PostgreSQL
    connection = psycopg2.connect(
        user="postgres",
        password="",
        host="localhost",
        port="5432",
        database=""  # Nome do banco de dados
    )
    cursor = connection.cursor()
    print("Conexão com o banco de dados estabelecida com sucesso!")

    # Solicitar ao usuário qual gráfico ele deseja ver
    escolha = input("Qual gráfico você deseja ver? (1: Região Onde Mora, 2: Gênero): ")

    if escolha == '1':
        # Análise de Região Onde Mora
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
            labels=df_regiao['regiao_onde_mora'], 
            autopct=lambda pct: func(pct, df_regiao['quantidade']),
            startangle=140, 
            pctdistance=0.85, 
            labeldistance=1.1,
            colors=colors
        )

        for text, wedge in zip(texts, wedges):
            text.set_color(wedge.get_facecolor())

        plt.title('Quantidade e Porcentagem de Registros por Região Onde Mora (Top 10)')
        plt.axis('equal')
        plt.show()

    elif escolha == '2':
        # Análise de Gênero
        query_genero = """
        SELECT genero, COUNT(*) AS quantidade
        FROM baseDeDados  
        GROUP BY genero
        ORDER BY quantidade DESC;
        """
        df_genero = pd.read_sql_query(query_genero, connection)

        # Substituir None por "Não especificado" na coluna de gênero
        df_genero['genero'] = df_genero['genero'].fillna('Não especificado')

        # Filtrar categorias pequenas para não sobrecarregar o gráfico
        df_genero = df_genero[df_genero['genero'] != 'Não especificado']

        # Calcular a porcentagem de cada gênero
        df_genero['percentual'] = (df_genero['quantidade'] / df_genero['quantidade'].sum()) * 100

        # Definir cores personalizadas
        cores_personalizadas = ['#ff9999', '#66b3ff']  # Vermelho, Azul para "Homem" e "Mulher"

        plt.figure(figsize=(8, 6))

        wedges, texts, autotexts = plt.pie(
            df_genero['percentual'], 
            labels=df_genero['genero'],  # Exibir rótulos diretamente no gráfico
            autopct=lambda pct: func(pct, df_genero['quantidade']),
            startangle=90,  # Começa em 90 graus para um estilo similar ao exemplo
            colors=cores_personalizadas,
            wedgeprops={'edgecolor': 'black'}
        )

        # Ajustar os rótulos de texto
        for autotext in autotexts:
            autotext.set_fontsize(14)
            autotext.set_color('white')
            autotext.set_weight('bold')

        # Adicionar título
        plt.title('Gráfico de gênero', fontsize=16)
        plt.show()

    else:
        print("Escolha inválida. Por favor, selecione 1 ou 2.")

except (Exception, psycopg2.Error) as error:
    print("Erro ao conectar ao PostgreSQL:", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("Conexão com o banco de dados encerrada.")
