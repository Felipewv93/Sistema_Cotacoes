import pandas as pd
import os

def salvar_excel(cotacoes):
    arquivo = 'data/cotacoes.xlsx'
    df_novo = pd.DataFrame([cotacoes])
    
    if os.path.exists(arquivo):
        df_existente = pd.read_excel(arquivo)
        df_final = pd.concat([df_existente, df_novo], ignore_index=True)
    else:
        df_final = df_novo
    
    df_final.to_excel(arquivo, index=False)
    print('Cotações salvas no arquivo Excel com sucesso!')
    return