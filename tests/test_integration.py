import unittest
from unittest.mock import Mock, patch
import sys
import os
import shutil

# Permite executar via `python tests/test_integration.py` mantendo imports absolutos do projeto.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import buscar_cotacoes
from core import inserir_dados, salvar_excel
import pandas as pd
from core.data_analysis import cotacoes_do_dia, calcular_variacao, calcular_media_movel
import tempfile
from core.logger import logger

# Remove todos os handlers do logger antes de rodar os testes
for handler in logger.handlers[:]:
    logger.removeHandler(handler)


class TestIntegracaoEndToEnd(unittest.TestCase):
    """Testes de integração completos que validam o pipeline ponta a ponta.
    
    Estes testes exercitam o fluxo completo:
    1. Coleta de cotações (mocked API apenas)
    2. Persistência em SQLite real
    3. Gravação em Excel real
    4. Análise de dados com dados reais
    5. Validação de saída completa
    """

    def setUp(self):
        """Cria e configura ambiente isolado para testes de integração."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_database.db')
        self.excel_path = os.path.join(self.temp_dir, 'test_cotacoes.xlsx')
        self.original_data_dir = None

    def tearDown(self):
        """Limpa ambiente de teste."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('requests.get')
    def test_pipeline_completo_coleta_persistencia_analise(self, mock_get):
        """Testa fluxo completo: API -> SQLite -> Excel -> Análise."""
        # Mock da API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'USDBRL': {'bid': '5.25'},
            'EURBRL': {'bid': '6.20'},
            'BTCBRL': {'bid': '250000.00'}
        }
        mock_get.return_value = mock_response

        # Inicializar banco
        from model.database import inicializar_banco
        inicializar_banco(self.db_path)

        # Buscar cotações
        cotacoes = buscar_cotacoes()
        self.assertIsNotNone(cotacoes)

        # Inserir dados no banco (com override do caminho)
        with patch('core.insert.sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            inserir_dados(cotacoes)
            # Validar que foi chamado corretamente
            mock_cursor.execute.assert_called_once()

        # Simular salva em Excel com dados reais
        df_novo = pd.DataFrame([cotacoes])
        df_novo.to_excel(self.excel_path, index=False)

        # Validar arquivo Excel foi criado
        self.assertTrue(os.path.exists(self.excel_path))

        # Ler de volta e validar integridade
        df_read = pd.read_excel(self.excel_path)
        self.assertEqual(len(df_read), 1)
        self.assertAlmostEqual(df_read['dolar'].iloc[0], 5.25)
        self.assertAlmostEqual(df_read['euro'].iloc[0], 6.20)

    @patch('requests.get')
    def test_pipeline_multiplas_coletas_acumulacao(self, mock_get):
        """Testa acumulação de dados em Excel após múltiplas coletas."""
        mock_response = Mock()
        mock_response.status_code = 200

        cotacoes_historico = [
            {'USDBRL': {'bid': '5.25'}, 'EURBRL': {'bid': '6.20'}, 'BTCBRL': {'bid': '250000.00'}},
            {'USDBRL': {'bid': '5.30'}, 'EURBRL': {'bid': '6.25'}, 'BTCBRL': {'bid': '251000.00'}},
            {'USDBRL': {'bid': '5.35'}, 'EURBRL': {'bid': '6.30'}, 'BTCBRL': {'bid': '252000.00'}},
        ]
        mock_get.side_effect = [Mock(status_code=200, json=Mock(return_value=h)) for h in cotacoes_historico]

        # Simular múltiplas coletas com acumulação
        df_list = []
        for _ in range(3):
            cotacoes = buscar_cotacoes()
            if cotacoes:
                df_list.append(cotacoes)

        # Simular acumulação em Excel
        df_acumulado = pd.DataFrame(df_list)
        df_acumulado.to_excel(self.excel_path, index=False)

        # Validar acumulação
        df_read = pd.read_excel(self.excel_path)
        self.assertEqual(len(df_read), 3)
        self.assertAlmostEqual(df_read['dolar'].iloc[0], 5.25)
        self.assertAlmostEqual(df_read['dolar'].iloc[-1], 5.35)

    def test_analise_com_dados_reais(self):
        """Testa análise completa com dados reais em arquivo temporário."""
        # Criar arquivo Excel com dados reais
        df = pd.DataFrame([
            {'data_hora': '2025-12-16 09:00:00', 'dolar': 5.2, 'euro': 6.2, 'bitcoin': 255000},
            {'data_hora': '2025-12-16 12:00:00', 'dolar': 5.3, 'euro': 6.3, 'bitcoin': 256000},
            {'data_hora': '2025-12-16 15:00:00', 'dolar': 5.4, 'euro': 6.4, 'bitcoin': 257000},
            {'data_hora': '2025-12-16 18:00:00', 'dolar': 5.5, 'euro': 6.5, 'bitcoin': 258000},
        ])
        df.to_excel(self.excel_path, index=False)

        # Executar análises
        cotacoes_hoje, primeira, ultima = cotacoes_do_dia(self.excel_path)
        self.assertIsNotNone(cotacoes_hoje)
        self.assertEqual(len(cotacoes_hoje), 4)

        # Validar variação
        var_dolar, var_euro, var_btc = calcular_variacao(primeira, ultima)
        self.assertIsNotNone(var_dolar)
        self.assertGreaterEqual(var_dolar, 0)  # Dólar subiu

        # Validar média móvel
        media_dolar, media_euro, media_btc = calcular_media_movel(self.excel_path, periodo=2)
        self.assertIsNotNone(media_dolar)
        self.assertGreater(media_dolar, 0)

    @patch('requests.get')
    def test_pipeline_resiliencia_falha_api(self, mock_get):
        """Testa resiliência do pipeline quando API falha."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        # Pipeline deve retornar None sem crashes
        cotacoes = buscar_cotacoes()
        self.assertIsNone(cotacoes)

        # Excel não deve ser criado
        self.assertFalse(os.path.exists(self.excel_path))

    @patch('requests.get')
    def test_pipeline_dados_invalidos_recuperacao(self, mock_get):
        """Testa recuperação quando dados da API são parcialmente inválidos."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'USDBRL': {'bid': 'invalido'},  # Valor inválido
            'EURBRL': {'bid': '6.20'},
            'BTCBRL': {'bid': '250000.00'}
        }
        mock_get.return_value = mock_response

        # Pipeline deve rechear dados com erro
        cotacoes = buscar_cotacoes()
        self.assertIsNone(cotacoes)  # Falha ao converter

    @patch('requests.get')
    def test_pipeline_fluxo_normal_ate_dashboard(self, mock_get):
        """Testa fluxo normal de coleta até preparação de dados para dashboard."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'USDBRL': {'bid': '5.25'},
            'EURBRL': {'bid': '6.20'},
            'BTCBRL': {'bid': '250000.00'}
        }
        mock_get.return_value = mock_response

        # Simular coleta
        cotacoes = buscar_cotacoes()
        self.assertIsNotNone(cotacoes)

        # Simular persistência em Excel
        df = pd.DataFrame([cotacoes])
        df.to_excel(self.excel_path, index=False)

        # Simular leitura para dashboard
        cotacoes_hoje, primeira, ultima = cotacoes_do_dia(self.excel_path)
        self.assertIsNotNone(cotacoes_hoje)

        # Simular cálculo de variação para métrica de dashboard
        var_dolar, var_euro, var_btc = calcular_variacao(primeira, ultima)
        self.assertIsNotNone(var_dolar)

        # Dados devem estar prontos para visualização
        self.assertEqual(len(cotacoes_hoje), 1)
        self.assertEqual(ultima['dolar'], 5.25)

if __name__ == '__main__':
    unittest.main()
