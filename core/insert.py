import sqlite3
from core import configurar_logger, logger

def inserir_dados(cotacoes):
    try:
        # Criar nova conexão para cada inserção (thread-safe)
        banco = sqlite3.connect('data/database.db')
        cursor = banco.cursor()
        
        cursor.execute(""" INSERT INTO cotacoes (data_hora, dolar, euro, bitcoin) 
                VALUES (?, ?, ?, ?) """,
                (cotacoes['data_hora'], cotacoes['dolar'], cotacoes['euro'], cotacoes['bitcoin'])
                )
        banco.commit()
        banco.close()
        logger.info('Cotações inseridas no banco de dados SQLite')

    except sqlite3.OperationalError as e:
        logger.error(f'Erro operacional no banco SQLite: {e}')
    except sqlite3.IntegrityError as e:
        logger.error(f'Erro de integridade no banco SQLite: {e}')
    except sqlite3.Error as e:
        logger.error(f'Erro ao inserir no banco SQLite: {e}')
    return