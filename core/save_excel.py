import pandas as pd
import os

def salvar_excel(cotacoes):
    try:
        arquivo = 'data/cotacoes.xlsx'
        df_novo = pd.DataFrame([cotacoes])
        
        if os.path.exists(arquivo):
            df_existente = pd.read_excel(arquivo)
            df_final = pd.concat([df_existente, df_novo], ignore_index=True)
        else:
            df_final = df_novo
        
        df_final.to_excel(arquivo, index=False)
        print('Cotações salvas no arquivo Excel com sucesso!')
    
    except PermissionError as e:
        print(f'Erro de permissão ao salvar o arquivo Excel: {e}')
    except Exception as e:
        print(f'Erro ao salvar o arquivo Excel: {e}')
    return