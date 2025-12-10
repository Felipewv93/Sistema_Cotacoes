import model
from api import buscar_cotacoes
from core import inserir_dados, salvar_excel, cotacoes_do_dia, calcular_variacao
from view import gerar_dashboard

def main():
    cotacoes = buscar_cotacoes()
    if cotacoes:
        inserir_dados(cotacoes)
        salvar_excel(cotacoes)
        cotacoes_hoje, primeira_cotacao, ultima_cotacao = cotacoes_do_dia('data/cotacoes.xlsx')
        calcular_variacao(primeira_cotacao, ultima_cotacao)

if __name__ == '__main__':
    main()