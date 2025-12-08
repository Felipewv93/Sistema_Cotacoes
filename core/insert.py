from model import cursor, banco
import sqlite3

def inserir_dados(cotacoes):
    try:
        cursor.execute(""" INSERT INTO cotacoes (data_hora, dolar, euro, bitcoin) 
                VALUES (?, ?, ?, ?) """,
                (cotacoes['data_hora'], cotacoes['dolar'], cotacoes['euro'], cotacoes['bitcoin'])
                )
        banco.commit()
        print('Cotações inseridas no banco de dados com sucesso!')

    except sqlite3.OperationalError as e:
        banco.rollback()
        print(f'Erro operacional ao inserir dados no banco: {e}')
    except sqlite3.IntegrityError as e:
        banco.rollback()
        print(f'Erro de integridade ao inserir dados no banco: {e}')
    except sqlite3.Error as e:
        banco.rollback()
        print(f'Erro ao inserir dados no banco de dados: {e}')
    return