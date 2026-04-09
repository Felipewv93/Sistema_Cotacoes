# Sistema de Coleta e Monitoramento de Cotações

Pipeline em Python para captura, persistência e visualização de cotações de moedas e criptomoedas em tempo real. O projeto coleta dados da AwesomeAPI, registra as informações em SQLite e Excel, e disponibiliza uma interface analítica com Streamlit e Plotly.

## Visão Geral

Este projeto foi desenvolvido com foco em um fluxo simples, observável e reproduzível de dados. Ele demonstra boas práticas comuns em engenharia de dados, como ingestão automatizada, armazenamento incremental, análise temporal e disponibilização de métricas para consumo rápido.

### Destaques técnicos

- Ingestão automatizada de cotações via API REST
- Persistência em SQLite para histórico estruturado
- Exportação incremental para planilha Excel
- Logs de execução para rastreabilidade e diagnóstico
- Análise temporal com variação diária e média móvel
- Dashboard interativo para acompanhamento dos dados

## Arquitetura

Fluxo principal:

1. Consulta à AwesomeAPI para obter cotações de Dólar, Euro e Bitcoin
2. Normalização dos dados retornados pela API
3. Persistência em SQLite
4. Gravação incremental em Excel
5. Cálculo de indicadores analíticos
6. Exibição dos resultados no dashboard

## Funcionalidades

### Coleta e persistência

- Coleta cotações em tempo real de USD, EUR e BTC em relação ao BRL
- Registra data e hora de cada captura
- Persiste os dados em banco SQLite
- Mantém histórico em planilha Excel sem sobrescrever registros anteriores

### Análise de dados

- Filtra as cotações do dia atual
- Calcula a variação percentual entre a primeira e a última leitura do dia
- Calcula média móvel com janela padrão de 7 dias
- Identifica automaticamente as últimas cotações diárias para análise histórica

### Visualização

- Dashboard interativo com Streamlit
- Gráficos de linha para evolução temporal
- Comparação visual entre moedas com Plotly
- Gráfico de barras para variação percentual diária
- Tabela detalhada com os registros mais recentes

## Stack Utilizada

- Python 3.x
- requests para consumo da API
- pandas para manipulação e análise de dados
- openpyxl para exportação em Excel
- sqlite3 para persistência local
- streamlit para interface analítica
- plotly para visualização interativa
- APScheduler para automação periódica

## Estrutura do Projeto

```
├── main.py
├── scheduler.py
├── requirements.txt
├── README.md
├── api/
│   └── request.py
├── core/
│   ├── data_analysis.py
│   ├── insert.py
│   ├── logger.py
│   └── save_excel.py
├── model/
│   └── database.py
├── view/
│   └── dashboard.py
├── data/
└── logs/
```

## Fonte de Dados

O projeto utiliza a AwesomeAPI Economia:

- Endpoint: https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,BTC-BRL
- Documentação: https://docs.awesomeapi.com.br

## Armazenamento

### SQLite

- Arquivo: `data/database.db`
- Tabela principal: `cotacoes`
- Campos: `id`, `data_hora`, `dolar`, `euro`, `bitcoin`

### Excel

- Arquivo: `data/cotacoes.xlsx`
- Cada linha representa uma coleta executada
- Atualização em modo append, preservando o histórico

## Como Executar

### Instalação

```bash
pip install -r requirements.txt
```

### Execução da coleta

```bash
python main.py
```

Esse comando realiza uma coleta única, persiste os dados e atualiza a planilha Excel.

### Execução do dashboard

```bash
streamlit run view/dashboard.py
```

### Execução dos testes

```bash
pytest
```

Opcionalmente, para saída detalhada:

```bash
pytest -v
```

## Automação

O arquivo `scheduler.py` executa coletas automáticas de segunda a sexta, das 9h às 18h, em intervalos de 1 hora. Isso simula um pipeline recorrente de ingestão, útil para acompanhar a evolução dos dados ao longo do dia.

## Resultado Gerado

Para cada execução, o sistema registra:

| Campo | Descrição |
| --- | --- |
| `data_hora` | Data e hora da coleta |
| `dolar` | Cotação do Dólar (USD → BRL) |
| `euro` | Cotação do Euro (EUR → BRL) |
| `bitcoin` | Cotação do Bitcoin (BTC → BRL) |

## Observações

- É necessária conexão com a internet para consumir a API
- O banco de dados e a planilha são criados automaticamente na primeira execução
- Os registros anteriores são preservados a cada nova coleta
- Os logs são gravados em `logs/app.log`

## Evoluções Futuras

- Ingestão de histórico para janelas maiores de análise
- Adição de novas moedas e ativos digitais
- Métricas adicionais de tendência e volatilidade
- Testes automatizados para as rotinas principais
- Versionamento e observabilidade mais robustos para cenários de produção

## Autor

Felipe Viana
