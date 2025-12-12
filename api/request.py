import requests
from datetime import datetime
from core import configurar_logger, logger


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
                logger.info(f"Cotações obtidas - Dólar: R$ {cotacoes['dolar']:.4f}, Euro: R$ {cotacoes['euro']:.4f}, Bitcoin: R$ {cotacoes['bitcoin']:.2f}")
                return cotacoes
            except KeyError as e:
                logger.error(f'Chave esperada não encontrada nos dados da API: {e}')
                return None
            except (ValueError, TypeError) as e:
                logger.error(f'Não foi possível converter valores para float: {e}')
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
        logger.error(f'Erro de conexão com a API: {e}')
        return None
    except requests.exceptions.Timeout as e:
        logger.warning(f'Timeout na requisição à API: {e}')
        return None
    except Exception as e:
        logger.error(f'Erro na requisição: {e}')
        return None