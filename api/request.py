import requests
from datetime import datetime


url = 'https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,BTC-BRL'

def buscar_cotacoes():
    response = requests.get(url)
    dados = response.json()
    cotacoes = {
        'dolar': float(dados['USDBRL']['bid']),
        'euro': float(dados['EURBRL']['bid']),
        'bitcoin': float(dados['BTCBRL']['bid']),
        'data_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return cotacoes