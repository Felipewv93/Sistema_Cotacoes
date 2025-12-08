import requests
from datetime import datetime


url = 'https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,BTC-BRL'

def buscar_cotacoes():
    try:
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            
            try:
                cotacoes = {
                    'dolar': float(dados['USDBRL']['bid']),
                    'euro': float(dados['EURBRL']['bid']),
                    'bitcoin': float(dados['BTCBRL']['bid']),
                    'data_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                return cotacoes
            except KeyError as e:
                print(f'Erro: Chave esperada não encontrada nos dados da API: {e}')
                return None
            except (ValueError, TypeError) as e:
                print(f'Erro: Não foi possível converter os valores para float: {e}')
                return None
                
        elif response.status_code == 400:
            raise Exception(f"Erro 400: Requisição inválida. Verifique os parâmetros enviados.")
        elif response.status_code == 404:
            raise Exception(f"Erro 404: Recurso não encontrado. Verifique a URL: {url}")
        elif response.status_code == 500:
            raise Exception(f"Erro 500: Erro interno do servidor. Tente novamente mais tarde.")
        else:
            raise Exception(f"Erro {response.status_code}: Não foi possível obter as cotações.")
    except requests.exceptions.ConnectionError as e:
        print(f'Erro de conexão. Detalhes: {e}')
        return None
    except requests.exceptions.Timeout as e:
        print(f'Erro de timeout: A requisição demorou muito para responder. Detalhes: {e}')
        return None
    except Exception as e:
        print(f'Erro na requisição: {e}')
        return None