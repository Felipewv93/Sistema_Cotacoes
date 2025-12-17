import unittest
from unittest.mock import Mock, patch
from api import buscar_cotacoes
from core import inserir_dados, salvar_excel
import pandas as pd
from core.data_analysis import cotacoes_do_dia, calcular_variacao, calcular_media_movel
import tempfile
import os
from core.logger import logger

# Remove todos os handlers do logger antes de rodar os testes
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

class TestRequisicoesAPI(unittest.TestCase):

    @patch('requests.get')
    def test_buscar_cotacoes(self, mock_get):
        mock_response = Mock()
        # Simula resposta real da API
        expected_data = {
            'USDBRL': {'bid': '5.25'},
            'EURBRL': {'bid': '6.20'},
            'BTCBRL': {'bid': '250000.00'}
        }
        mock_response.json.return_value = expected_data
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        cotacoes = buscar_cotacoes()
        self.assertIsNotNone(cotacoes)
        self.assertEqual(cotacoes['dolar'], 5.25)
        self.assertEqual(cotacoes['euro'], 6.20)
        self.assertEqual(cotacoes['bitcoin'], 250000.00)
        print("Teste buscar_cotacoes passou com sucesso.")


# Teste de inserção pode ser feito apenas verificando se não lança exceção
class TestFuncoesInsercaoDados(unittest.TestCase):
    @patch('sqlite3.connect')
    def test_inserir_dados(self, mock_connect):
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        cotacoes = {
            'dolar': 5.25,
            'euro': 6.20,
            'bitcoin': 250000.00,
            'data_hora': '2025-12-16 10:00:00'
        }
        try:
            inserir_dados(cotacoes)
            mock_connect.assert_called_once()
            mock_conn.cursor.assert_called_once()
            mock_cursor.execute.assert_called_once()
            mock_conn.commit.assert_called_once()
            mock_conn.close.assert_called_once()
            print("Teste inserir_dados passou com sucesso.")
        except Exception as e:
            self.fail(f'inserir_dados lançou uma exceção: {e}')

# Teste de salvar_excel pode ser feito apenas verificando se não lança exceção
class TestSalvarExcel(unittest.TestCase):
    @patch('pandas.DataFrame.to_excel')
    @patch('pandas.read_excel', return_value=None)
    @patch('os.path.exists', return_value=False)
    def test_salvar_excel(self, _, __, mock_to_excel):
        cotacoes = {
            'dolar': 5.25,
            'euro': 6.20,
            'bitcoin': 250000.00,
            'data_hora': '2025-12-16 10:00:00'
        }
        try:
            salvar_excel(cotacoes)
            mock_to_excel.assert_called_once()
            print("Teste salvar_excel passou com sucesso.")
        except Exception as e:
            self.fail(f'salvar_excel lançou uma exceção: {e}')

class TestFuncoesAnalise(unittest.TestCase):
    def setUp(self):
        
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        df = pd.DataFrame([
            {'data_hora': '2025-12-15 09:00:00', 'dolar': 5.0, 'euro': 6.0, 'bitcoin': 250000},
            {'data_hora': '2025-12-15 18:00:00', 'dolar': 5.5, 'euro': 6.5, 'bitcoin': 260000},
            {'data_hora': '2025-12-16 09:00:00', 'dolar': 5.2, 'euro': 6.2, 'bitcoin': 255000},
            {'data_hora': '2025-12-16 18:00:00', 'dolar': 5.7, 'euro': 6.7, 'bitcoin': 265000},
        ])
        df.to_excel(self.temp_file.name, index=False)

    def tearDown(self):
        self.temp_file.close()
        os.unlink(self.temp_file.name)


    def test_cotacoes_do_dia(self):
        cotacoes_hoje, primeira, ultima = cotacoes_do_dia(self.temp_file.name)
        self.assertIsNotNone(cotacoes_hoje)
        # O comportamento correto é pegar a última cotação do dia mais recente
        self.assertEqual(primeira['dolar'], 5.2)
        self.assertEqual(ultima['dolar'], 5.7)
        print("Teste cotacoes_do_dia passou com sucesso.")

    def test_calcular_variacao(self):
        primeira = {'dolar': 5.0, 'euro': 6.0, 'bitcoin': 250000}
        ultima = {'dolar': 5.5, 'euro': 6.5, 'bitcoin': 260000}
        var_dolar, var_euro, var_btc = calcular_variacao(primeira, ultima)
        self.assertAlmostEqual(var_dolar, 10.0)
        self.assertAlmostEqual(var_euro, 8.333333, places=4)
        self.assertAlmostEqual(var_btc, 4.0)
        print("Teste calcular_variacao passou com sucesso.")

    def test_calcular_media_movel(self):
        media_dolar, media_euro, media_btc = calcular_media_movel(self.temp_file.name, periodo=2)
        # O cálculo correto pega as duas últimas datas (última cotação de cada dia): 5.5 e 5.7
        self.assertAlmostEqual(media_dolar, (5.5+5.7)/2)
        self.assertAlmostEqual(media_euro, (6.5+6.7)/2)
        self.assertAlmostEqual(media_btc, (260000+265000)/2)
        print("Teste calcular_media_movel passou com sucesso.")

    @patch('builtins.print')
    def test_cotacoes_do_dia_arquivo_inexistente(self, _):
        cotacoes_hoje, primeira, ultima = cotacoes_do_dia('arquivo_inexistente.xlsx')
        self.assertIsNone(cotacoes_hoje)
        self.assertIsNone(primeira)
        self.assertIsNone(ultima)

    @patch('builtins.print')
    def test_calcular_media_movel_arquivo_inexistente(self, _):
        media_dolar, media_euro, media_btc = calcular_media_movel('arquivo_inexistente.xlsx', periodo=2)
        self.assertIsNone(media_dolar)
        self.assertIsNone(media_euro)
        self.assertIsNone(media_btc)

if __name__ == '__main__':
        unittest.main()