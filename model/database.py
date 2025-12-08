import sqlite3
import os

if not os.path.exists('data'):
    os.makedirs('data')

try:
    banco = sqlite3.connect('data/database.db')
    cursor = banco.cursor()

    cursor.execute(""" CREATE TABLE IF NOT EXISTS cotacoes 
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_hora TEXT,
                dolar REAL,
                euro REAL,
                bitcoin REAL) """)
    banco.commit()

except sqlite3.OperationalError as e:
    print(f'Erro operacional ao conectar ou criar o banco de dados: {e}')

except PermissionError as e:
    print(f'Erro de permissão ao acessar o banco de dados: {e}')

except sqlite3.Error as e:
    print(f'Erro no SQLite: {e}')