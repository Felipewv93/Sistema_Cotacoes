import model
from api import buscar_cotacoes
from core import inserir_dados, salvar_excel

def main():
    cotacoes = buscar_cotacoes()
    inserir_dados(cotacoes)
    salvar_excel(cotacoes)

if __name__ == '__main__':
    main()