import pandas as pd
import os


def cotacoes_do_dia(arquivo='data/cotacoes.xlsx'):
    if os.path.exists(arquivo):
        df = pd.read_excel(arquivo)
        
        df['data_hora'] = pd.to_datetime(df['data_hora'])
        data_hoje = df['data_hora'].max().date()
        cotacoes_hoje = df[df['data_hora'].dt.date == data_hoje]
        
        if len(cotacoes_hoje) > 0:
            primeira_cotacao = cotacoes_hoje.iloc[0]
            ultima_cotacao = cotacoes_hoje.iloc[-1] 
            return cotacoes_hoje, primeira_cotacao, ultima_cotacao
        
        else:
            print("Não há cotações registradas para hoje.")
            return None, None, None

    else:
        print("O arquivo 'data/cotacoes.xlsx' não existe.")

        return None, None, None

def calcular_variacao(primeira_cotacao, ultima_cotacao):
    if primeira_cotacao is not None and ultima_cotacao is not None:
        variacao_dolar = (ultima_cotacao['dolar'] - primeira_cotacao['dolar']) * 100 / primeira_cotacao['dolar']
        variacao_euro = (ultima_cotacao['euro'] - primeira_cotacao['euro']) * 100 / primeira_cotacao['euro']
        variacao_bitcoin = (ultima_cotacao['bitcoin'] - primeira_cotacao['bitcoin']) * 100 / primeira_cotacao['bitcoin']
        return variacao_dolar, variacao_euro, variacao_bitcoin
  
    else:
        print("Não foi possível calcular a variação, pois as cotações não foram encontradas.")
        return None, None, None
    
def calcular_media_movel(arquivo='data/cotacoes.xlsx', periodo=7):
    if os.path.exists(arquivo):
        df = pd.read_excel(arquivo)
        df['data_hora'] = pd.to_datetime(df['data_hora'])
        
        df['data'] = df['data_hora'].dt.date
        df = df.sort_values(by='data_hora')
        
        ultimas_cotacoes = df.groupby('data').last().reset_index()
        
        ultimas_cotacoes_periodo = ultimas_cotacoes.tail(periodo)
        
        media_movel_dolar = ultimas_cotacoes_periodo['dolar'].mean()
        media_movel_euro = ultimas_cotacoes_periodo['euro'].mean()
        media_movel_bitcoin = ultimas_cotacoes_periodo['bitcoin'].mean()
        
        return media_movel_dolar, media_movel_euro, media_movel_bitcoin
    else:
        print("O arquivo 'data/cotacoes.xlsx' não existe.")
        return None, None, None