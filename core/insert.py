import sqlite3
from core.logger import logger
from core.validation import validar_cotacoes

def inserir_dados(cotacoes):
    cotacoes_validas = validar_cotacoes(cotacoes)
    if cotacoes_validas is None:
        logger.error('Inserção cancelada: payload de cotações inválido')
        return

    banco = None
    try:
        # Criar nova conexão para cada inserção (thread-safe)
        banco = sqlite3.connect('data/database.db')
        cursor = banco.cursor()
        cursor.execute('BEGIN')
        
        cursor.execute(""" INSERT INTO cotacoes (data_hora, dolar, euro, bitcoin) 
                VALUES (?, ?, ?, ?) """,
                (
                    cotacoes_validas['data_hora'],
                    cotacoes_validas['dolar'],
                    cotacoes_validas['euro'],
                    cotacoes_validas['bitcoin'],
                )
                )
        banco.commit()
        logger.info('Cotações inseridas no banco de dados SQLite')

    except sqlite3.OperationalError as e:
        if banco is not None:
            banco.rollback()
        logger.error(f'Erro operacional no banco SQLite: {e}')
    except sqlite3.IntegrityError as e:
        if banco is not None:
            banco.rollback()
        logger.error(f'Erro de integridade no banco SQLite: {e}')
    except sqlite3.Error as e:
        if banco is not None:
            banco.rollback()
        logger.error(f'Erro ao inserir no banco SQLite: {e}')
    finally:
        if banco is not None:
            banco.close()
    return