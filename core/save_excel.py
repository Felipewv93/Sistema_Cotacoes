import pandas as pd
import os
from core import configurar_logger, logger

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
        logger.info(f'Cotações salvas no Excel (total: {len(df_final)} registros)')
    
    except PermissionError as e:
        logger.error(f'Erro de permissão ao salvar Excel: {e}')
    except Exception as e:
        logger.error(f'Erro ao salvar Excel: {e}')
    return