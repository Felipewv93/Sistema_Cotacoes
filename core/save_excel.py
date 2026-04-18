import pandas as pd
import os
from core.logger import logger
from core.validation import validar_cotacoes

def salvar_excel(cotacoes):
    cotacoes_validas = validar_cotacoes(cotacoes)
    if cotacoes_validas is None:
        logger.error('Salvamento cancelado: payload de cotações inválido')
        return

    try:
        arquivo = 'data/cotacoes.xlsx'
        df_novo = pd.DataFrame([cotacoes_validas])
        
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