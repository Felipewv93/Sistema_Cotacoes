import sqlite3

banco = sqlite3.connect('data/database.db')

cursor = banco.cursor()

cursor.execute(""" CREATE TABLE IF NOT EXISTS cotacoes 
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
               data_hora TEXT,
               dolar REAL,
               euro REAL,
               bitcoin REAL) """)

banco.commit()