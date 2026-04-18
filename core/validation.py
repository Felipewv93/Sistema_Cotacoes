import math

from core.logger import logger


REQUIRED_FIELDS = ("data_hora", "dolar", "euro", "bitcoin")


def validar_cotacoes(cotacoes):
    if not isinstance(cotacoes, dict):
        logger.error("Payload inválido: esperado dicionário de cotações")
        return None

    campos_faltantes = [campo for campo in REQUIRED_FIELDS if campo not in cotacoes]
    if campos_faltantes:
        logger.error(f"Payload inválido: campos ausentes {campos_faltantes}")
        return None

    data_hora = cotacoes.get("data_hora")
    if not isinstance(data_hora, str) or not data_hora.strip():
        logger.error("Payload inválido: data_hora deve ser uma string não vazia")
        return None

    try:
        dolar = float(cotacoes.get("dolar"))
        euro = float(cotacoes.get("euro"))
        bitcoin = float(cotacoes.get("bitcoin"))
    except (TypeError, ValueError):
        logger.error("Payload inválido: valores de moeda devem ser numéricos")
        return None

    if not all(math.isfinite(valor) for valor in (dolar, euro, bitcoin)):
        logger.error("Payload inválido: valores de moeda devem ser finitos")
        return None

    return {
        "data_hora": data_hora.strip(),
        "dolar": dolar,
        "euro": euro,
        "bitcoin": bitcoin,
    }