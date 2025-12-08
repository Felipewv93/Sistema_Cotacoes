from model import cursor, banco

def inserir_dados(cotacoes):
    cursor.execute(""" INSERT INTO cotacoes (data_hora, dolar, euro, bitcoin) 
               VALUES (?, ?, ?, ?) """,
               (cotacoes['data_hora'], cotacoes['dolar'], cotacoes['euro'], cotacoes['bitcoin'])
               )
    banco.commit()
    print('Cotações inseridas no banco de dados com sucesso!')
    return