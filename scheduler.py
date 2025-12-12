from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import model
from api import buscar_cotacoes
from core import inserir_dados, salvar_excel
from core import configurar_logger, logger

def automatizar_cotacoes():
    logger.info("Iniciando coleta automática de cotações (Scheduler)")
    cotacoes = buscar_cotacoes()
    if cotacoes:
        inserir_dados(cotacoes)
        salvar_excel(cotacoes)
        logger.info("Coleta automática finalizada com sucesso")
    else:
        logger.error("Falha na coleta automática de cotações")

scheduler = BlockingScheduler()


scheduler.add_job(
    automatizar_cotacoes,
    'cron',
    day_of_week='mon-fri',
    hour='9-18',
    minute=0 ,
)

print("=" * 60)
print("Scheduler iniciado!")
print("Horário de coleta: Segunda a Sexta, das 9h às 18h (de hora em hora)")
print("Pressione Ctrl+C para parar.")
print("=" * 60)

scheduler.start()