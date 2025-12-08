import pandas as pd
import os


if os.path.exists('data/cotacoes.xlsx'):
    df = pd.read_excel('data/cotacoes.xlsx')
    dia_hj = df['data_hora'].max().split(' ')[0][8:10]
    for i in range(len(df)):
        dia = df['data_hora'][i][8:10]
        if dia == dia_hj:
            print(f"Dólar: {df['dolar'][i]}")
            print(f"Euro: {df['euro'][i]}")
            print(f"Bitcoin: {df['bitcoin'][i]}")
else:
    print("O arquivo 'data/cotacoes.xlsx' não existe.")