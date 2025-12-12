import model
from core import configurar_logger, logger
from api import buscar_cotacoes
from core import inserir_dados, salvar_excel

def main():
    logger.info("==== Iniciando coleta de cotações ====")
    cotacoes = buscar_cotacoes()
    if cotacoes:
        inserir_dados(cotacoes)
        salvar_excel(cotacoes)
        logger.info("==== Coleta finalizada com sucesso ====")
    else:
        logger.error("Falha ao buscar cotações. Processo interrompido.")

if __name__ == '__main__':
    main()