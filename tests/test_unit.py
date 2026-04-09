import unittest
from unittest.mock import Mock, patch
import sys
import os
import sqlite3
import requests
import importlib

# Permite executar via `python tests/test_unit.py` mantendo imports absolutos do projeto.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api import buscar_cotacoes
from core import inserir_dados, salvar_excel
import pandas as pd
from core.data_analysis import cotacoes_do_dia, calcular_variacao, calcular_media_movel
import tempfile
from core.logger import logger


class DummyContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class DummyFigure:
    def add_trace(self, *args, **kwargs):
        return None

    def update_layout(self, *args, **kwargs):
        return None

    def update_traces(self, *args, **kwargs):
        return None

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

    @patch('api.request.logger.error')
    @patch('requests.get')
    def test_buscar_cotacoes_status_400(self, mock_get, _):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response

        cotacoes = buscar_cotacoes()
        self.assertIsNone(cotacoes)

    @patch('api.request.logger.error')
    @patch('requests.get')
    def test_buscar_cotacoes_status_404(self, mock_get, _):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        cotacoes = buscar_cotacoes()
        self.assertIsNone(cotacoes)

    @patch('api.request.logger.error')
    @patch('requests.get')
    def test_buscar_cotacoes_status_500(self, mock_get, _):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        cotacoes = buscar_cotacoes()
        self.assertIsNone(cotacoes)

    @patch('api.request.logger.error')
    @patch('requests.get')
    def test_buscar_cotacoes_status_desconhecido(self, mock_get, _):
        mock_response = Mock()
        mock_response.status_code = 418
        mock_get.return_value = mock_response

        cotacoes = buscar_cotacoes()
        self.assertIsNone(cotacoes)

    @patch('api.request.logger.error')
    @patch('requests.get')
    def test_buscar_cotacoes_chave_invalida(self, mock_get, _):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'USDBRL': {'bid': '5.25'}
        }
        mock_get.return_value = mock_response

        cotacoes = buscar_cotacoes()
        self.assertIsNone(cotacoes)

    @patch('api.request.logger.error')
    @patch('requests.get')
    def test_buscar_cotacoes_valor_invalido(self, mock_get, _):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'USDBRL': {'bid': 'abc'},
            'EURBRL': {'bid': '6.20'},
            'BTCBRL': {'bid': '250000.00'}
        }
        mock_get.return_value = mock_response

        cotacoes = buscar_cotacoes()
        self.assertIsNone(cotacoes)

    @patch('api.request.logger.warning')
    @patch('requests.get', side_effect=requests.exceptions.Timeout('timeout'))
    def test_buscar_cotacoes_timeout(self, _, mock_warning):
        cotacoes = buscar_cotacoes()
        self.assertIsNone(cotacoes)
        mock_warning.assert_called_once()

    @patch('api.request.logger.error')
    @patch('requests.get', side_effect=requests.exceptions.ConnectionError('sem conexão'))
    def test_buscar_cotacoes_connection_error(self, _, mock_error):
        cotacoes = buscar_cotacoes()
        self.assertIsNone(cotacoes)
        mock_error.assert_called_once()


# Teste de inserção feito verificando se não lança exceção
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

    @patch('core.insert.logger.error')
    @patch('core.insert.sqlite3.connect', side_effect=sqlite3.OperationalError('erro operacional'))
    def test_inserir_dados_operational_error(self, _, mock_error):
        cotacoes = {
            'dolar': 5.25,
            'euro': 6.20,
            'bitcoin': 250000.00,
            'data_hora': '2025-12-16 10:00:00'
        }
        inserir_dados(cotacoes)
        mock_error.assert_called_once()

    @patch('core.insert.logger.error')
    @patch('core.insert.sqlite3.connect', side_effect=sqlite3.IntegrityError('erro integridade'))
    def test_inserir_dados_integrity_error(self, _, mock_error):
        cotacoes = {
            'dolar': 5.25,
            'euro': 6.20,
            'bitcoin': 250000.00,
            'data_hora': '2025-12-16 10:00:00'
        }
        inserir_dados(cotacoes)
        mock_error.assert_called_once()

    @patch('core.insert.logger.error')
    @patch('core.insert.sqlite3.connect', side_effect=sqlite3.DatabaseError('erro sqlite'))
    def test_inserir_dados_sqlite_error_generico(self, _, mock_error):
        cotacoes = {
            'dolar': 5.25,
            'euro': 6.20,
            'bitcoin': 250000.00,
            'data_hora': '2025-12-16 10:00:00'
        }
        inserir_dados(cotacoes)
        mock_error.assert_called_once()

# Teste de salvar_excel feito verificando se não lança exceção
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

    @patch('pandas.DataFrame.to_excel')
    @patch('pandas.read_excel')
    @patch('os.path.exists', return_value=True)
    def test_salvar_excel_arquivo_existente(self, _, mock_read_excel, mock_to_excel):
        mock_read_excel.return_value = pd.DataFrame([
            {'dolar': 5.00, 'euro': 6.00, 'bitcoin': 240000.0, 'data_hora': '2025-12-15 10:00:00'}
        ])
        cotacoes = {
            'dolar': 5.25,
            'euro': 6.20,
            'bitcoin': 250000.00,
            'data_hora': '2025-12-16 10:00:00'
        }
        salvar_excel(cotacoes)
        mock_read_excel.assert_called_once()
        mock_to_excel.assert_called_once()

    @patch('core.save_excel.logger.error')
    @patch('pandas.DataFrame.to_excel', side_effect=PermissionError('sem permissão'))
    @patch('os.path.exists', return_value=False)
    def test_salvar_excel_permission_error(self, _, __, mock_error):
        cotacoes = {
            'dolar': 5.25,
            'euro': 6.20,
            'bitcoin': 250000.00,
            'data_hora': '2025-12-16 10:00:00'
        }
        salvar_excel(cotacoes)
        mock_error.assert_called_once()

    @patch('core.save_excel.logger.error')
    @patch('pandas.DataFrame.to_excel', side_effect=RuntimeError('erro genérico'))
    @patch('os.path.exists', return_value=False)
    def test_salvar_excel_erro_generico(self, _, __, mock_error):
        cotacoes = {
            'dolar': 5.25,
            'euro': 6.20,
            'bitcoin': 250000.00,
            'data_hora': '2025-12-16 10:00:00'
        }
        salvar_excel(cotacoes)
        mock_error.assert_called_once()

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

    @patch('builtins.print')
    def test_calcular_variacao_sem_dados(self, _):
        var_dolar, var_euro, var_btc = calcular_variacao(None, None)
        self.assertIsNone(var_dolar)
        self.assertIsNone(var_euro)
        self.assertIsNone(var_btc)

    def test_calcular_media_movel(self):
        media_dolar, media_euro, media_btc = calcular_media_movel(self.temp_file.name, periodo=2)
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


class TestFluxoMain(unittest.TestCase):
    @patch('main.logger')
    @patch('main.salvar_excel')
    @patch('main.inserir_dados')
    @patch('main.buscar_cotacoes')
    def test_main_fluxo_sucesso(self, mock_buscar, mock_inserir, mock_salvar, mock_logger):
        mock_buscar.return_value = {
            'dolar': 5.25,
            'euro': 6.20,
            'bitcoin': 250000.00,
            'data_hora': '2025-12-16 10:00:00'
        }

        import main
        main.main()

        mock_inserir.assert_called_once()
        mock_salvar.assert_called_once()
        self.assertEqual(mock_logger.info.call_count, 2)

    @patch('main.logger')
    @patch('main.salvar_excel')
    @patch('main.inserir_dados')
    @patch('main.buscar_cotacoes', return_value=None)
    def test_main_fluxo_falha(self, _, mock_inserir, mock_salvar, mock_logger):
        import main
        main.main()

        mock_inserir.assert_not_called()
        mock_salvar.assert_not_called()
        mock_logger.error.assert_called_once()


class TestScheduler(unittest.TestCase):
    @patch('scheduler.logger')
    @patch('scheduler.salvar_excel')
    @patch('scheduler.inserir_dados')
    @patch('scheduler.buscar_cotacoes')
    def test_automatizar_cotacoes_sucesso(self, mock_buscar, mock_inserir, mock_salvar, mock_logger):
        mock_buscar.return_value = {
            'dolar': 5.25,
            'euro': 6.20,
            'bitcoin': 250000.00,
            'data_hora': '2025-12-16 10:00:00'
        }

        import scheduler
        scheduler.automatizar_cotacoes()

        mock_inserir.assert_called_once()
        mock_salvar.assert_called_once()
        self.assertEqual(mock_logger.info.call_count, 2)

    @patch('scheduler.logger')
    @patch('scheduler.salvar_excel')
    @patch('scheduler.inserir_dados')
    @patch('scheduler.buscar_cotacoes', return_value=None)
    def test_automatizar_cotacoes_falha(self, _, mock_inserir, mock_salvar, mock_logger):
        import scheduler
        scheduler.automatizar_cotacoes()

        mock_inserir.assert_not_called()
        mock_salvar.assert_not_called()
        mock_logger.error.assert_called_once()

    @patch('scheduler.BlockingScheduler')
    def test_configurar_scheduler(self, mock_scheduler_cls):
        mock_scheduler = Mock()
        mock_scheduler_cls.return_value = mock_scheduler

        import scheduler
        scheduler_instance = scheduler.configurar_scheduler()

        self.assertEqual(scheduler_instance, mock_scheduler)
        mock_scheduler.add_job.assert_called_once()

    @patch('builtins.print')
    @patch('scheduler.configurar_scheduler')
    def test_scheduler_main_chama_start(self, mock_configurar, _):
        mock_scheduler = Mock()
        mock_configurar.return_value = mock_scheduler

        import scheduler
        scheduler.main()

        mock_scheduler.start.assert_called_once()


class TestModelDatabase(unittest.TestCase):
    @patch('model.database.sqlite3.connect')
    @patch('model.database.os.path.exists', return_value=True)
    def test_database_inicializacao(self, _, mock_connect):
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        from model.database import inicializar_banco
        inicializar_banco('data/test.db')

        mock_connect.assert_called_once_with('data/test.db', check_same_thread=False)
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
        mock_conn.close.assert_called_once()

    @patch('builtins.print')
    @patch('model.database.sqlite3.connect', side_effect=sqlite3.OperationalError('erro operacional'))
    @patch('model.database.os.path.exists', return_value=True)
    def test_database_operational_error(self, _, __, mock_print):
        from model.database import inicializar_banco

        inicializar_banco()
        mock_print.assert_called_once()

    @patch('builtins.print')
    @patch('model.database.sqlite3.connect', side_effect=PermissionError('sem permissao'))
    @patch('model.database.os.path.exists', return_value=True)
    def test_database_permission_error(self, _, __, mock_print):
        from model.database import inicializar_banco

        inicializar_banco()
        mock_print.assert_called_once()

    @patch('builtins.print')
    @patch('model.database.sqlite3.connect', side_effect=sqlite3.DatabaseError('erro sqlite'))
    @patch('model.database.os.path.exists', return_value=True)
    def test_database_sqlite_error(self, _, __, mock_print):
        from model.database import inicializar_banco

        inicializar_banco()
        mock_print.assert_called_once()


class TestDashboard(unittest.TestCase):
    @patch('view.dashboard.st.error')
    @patch('view.dashboard.st.title')
    @patch('view.dashboard.st.markdown')
    @patch('view.dashboard.st.set_page_config')
    @patch('view.dashboard.cotacoes_do_dia', return_value=(None, None, None))
    def test_dashboard_sem_dados(self, _, __, ___, ____, mock_error):
        import view.dashboard as dashboard

        dashboard.gerar_dashboard()
        mock_error.assert_called_once()

    @patch('view.dashboard.st.error')
    @patch('view.dashboard.st.title')
    @patch('view.dashboard.st.markdown')
    @patch('view.dashboard.st.set_page_config')
    @patch('view.dashboard.calcular_variacao', return_value=(None, None, None))
    @patch('view.dashboard.cotacoes_do_dia')
    def test_dashboard_sem_variacao(self, mock_cotacoes, _, __, ___, ____, mock_error):
        import view.dashboard as dashboard

        df = pd.DataFrame({'data_hora': pd.to_datetime(['2025-12-16 09:00:00']), 'dolar': [5.2], 'euro': [6.2], 'bitcoin': [255000]})
        mock_cotacoes.return_value = (df, df.iloc[0], df.iloc[0])

        dashboard.gerar_dashboard()
        mock_error.assert_called_once()

    @patch('view.dashboard.st.dataframe')
    @patch('view.dashboard.st.plotly_chart')
    @patch('view.dashboard.st.metric')
    @patch('view.dashboard.st.tabs', return_value=(DummyContext(), DummyContext(), DummyContext(), DummyContext()))
    @patch('view.dashboard.st.columns', return_value=(DummyContext(), DummyContext(), DummyContext()))
    @patch('view.dashboard.st.subheader')
    @patch('view.dashboard.st.error')
    @patch('view.dashboard.st.title')
    @patch('view.dashboard.st.markdown')
    @patch('view.dashboard.st.set_page_config')
    @patch('view.dashboard.go.Scatter', return_value=Mock())
    @patch('view.dashboard.go.Figure', return_value=DummyFigure())
    @patch('view.dashboard.px.bar', return_value=DummyFigure())
    @patch('view.dashboard.px.line', return_value=DummyFigure())
    @patch('view.dashboard.calcular_media_movel', return_value=(5.5, 6.5, 260000.0))
    @patch('view.dashboard.calcular_variacao', return_value=(1.2, -0.5, 2.7))
    @patch('view.dashboard.cotacoes_do_dia')
    def test_dashboard_fluxo_sucesso(self, mock_cotacoes, *_):
        import view.dashboard as dashboard

        df = pd.DataFrame({
            'data_hora': pd.to_datetime(['2025-12-16 09:00:00', '2025-12-16 18:00:00']),
            'dolar': [5.2, 5.7],
            'euro': [6.2, 6.7],
            'bitcoin': [255000, 265000]
        })
        mock_cotacoes.return_value = (df, df.iloc[0], df.iloc[-1])

        dashboard.gerar_dashboard()


class TestViewPackage(unittest.TestCase):
    def test_import_view_package(self):
        import view
        self.assertTrue(hasattr(view, 'gerar_dashboard'))

if __name__ == '__main__':
    unittest.main()
