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
        # Análise de Gênero
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

        # Definir cores personalizadas, adicione mais cores se necessário
        cores_personalizadas = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']  # Adicionar mais cores se houver mais categorias

        # Explodir todos os setores ligeiramente
        explode = [0.05 if genero == 'NULL' else 0 for genero in df_genero['genero']]

        plt.figure(figsize=(8, 6))

        wedges, texts, autotexts = plt.pie(
            df_genero['percentual'], 
            labels=None,  # Remover os rótulos diretamente no gráfico
            autopct=lambda pct: func(pct, df_genero['quantidade']),  # Mostrar porcentagem e quantidade para todas as categorias
            startangle=90,  # Começa em 90 graus para um estilo similar ao exemplo
            colors=cores_personalizadas,
            explode=explode,  # Explodir os setores
            wedgeprops={'edgecolor': 'black'},
            radius=1.2,  # Aumenta o tamanho do gráfico
        )

        # Criar um círculo no meio para transformar o gráfico de pizza em rosca
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        # Adicionar linhas para rótulos externos em categorias pequenas
        for i, txt in enumerate(autotexts):
            pct = df_genero['percentual'].iloc[i]
            if pct < 1:  # Limite para rótulos pequenos
                txt.set_position((0, 0))  # Movendo o rótulo para o centro
                txt.set_fontsize(0)  # Ocultar rótulo pequeno
                text = f"{df_genero['genero'].iloc[i]}: {func(pct, df_genero['quantidade'])}"
                plt.annotate(text, xy=wedges[i].center, xytext=(1.35, i*0.15), 
                             textcoords='data', ha='center', va='center',
                             bbox=dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white"),
                             arrowprops=dict(arrowstyle="-", color="black"))

        # Adicionar uma legenda separada para evitar sobreposição
        plt.legend(wedges, df_genero['genero'], title="Gêneros", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        # Adicionar título
        plt.title('Gráfico de Gênero', fontsize=16)

        plt.axis('equal')  # Assegura que o gráfico seja desenhado como um círculo
        plt.tight_layout()
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
