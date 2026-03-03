# Sistema de Coleta de Cotações

Sistema automatizado para coleta e armazenamento de cotações de moedas (Dólar, Euro e Bitcoin) em tempo real.

## Descrição

Este projeto busca cotações atualizadas de Dólar (USD), Euro (EUR) e Bitcoin (BTC) através da API AwesomeAPI e armazena os dados em:
- Banco de dados SQLite
- Arquivo Excel (.xlsx)

## Funcionalidades

### Coleta de Dados
- ✅ Busca de cotações em tempo real via API REST
- ✅ Armazenamento em banco de dados SQLite
- ✅ Exportação para planilha Excel
- ✅ Registro de data e hora de cada coleta
- ✅ Acumulação de dados (adiciona novas linhas sem sobrescrever)

### Análise de Dados
- ✅ Filtragem de cotações do dia atual
- ✅ Cálculo de variação percentual entre primeira e última cotação do dia
- ✅ Cálculo de média móvel (configurável, padrão 7 dias)
- ✅ Identificação automática da última cotação de cada dia

### Visualização
- ✅ Dashboard interativo com Streamlit
- ✅ Gráficos de linha para evolução das cotações
- ✅ Gráficos de barras para variações diárias
- ✅ Métricas em tempo real (valores atuais e variações)
- ✅ Visualização com Plotly (gráficos interativos)

## Estrutura do Projeto

```
projeto_dados/
│
├── main.py                 # Arquivo principal de execução
├── README.md               # Documentação do projeto
├── requirements.txt        # Dependências do projeto
├── scheduler.py            # Coleta automatizada de cotações
│
├── api/
│   └── request.py          # Requisições à API de cotações
│
├── core/
│   ├── insert.py           # Inserção de dados no banco
│   ├── save_excel.py       # Salvamento em Excel
│   ├── data_analysis.py    # Análise de dados (variações, médias móveis)
│   └── logger.py           # Sistema de logs
│
├── data/                   # Diretório para armazenamento
|   ├── database.db         # Banco de dados SQLite (gerado)
|   └── cotacoes.xlsx       # Planilha Excel (gerada)
|
├── logs/
│   └── app.log             # Logs gerados automaticamente
|
├── model/
│   ├── __init__.py         # Inicialização do módulo
│   └── database.py         # Configuração do banco de dados
│
└── view/
    └── dashboard.py        # Dashboard interativo com Streamlit
```

## Tecnologias Utilizadas

- **Python 3.x**
- **requests** - Requisições HTTP à API
- **pandas** - Manipulação de dados e Excel
- **openpyxl** - Engine para arquivos Excel
- **sqlite3** - Banco de dados (built-in)
- **streamlit** - Dashboard interativo
- **plotly** - Visualização de dados interativa

## Instalação

1. Clone o repositório ou baixe os arquivos do projeto

2. Instale as dependências necessárias:
```bash
pip install -r requirements.txt
```

3. Certifique-se de que a pasta `data/` existe (será criada automaticamente ao executar)

## Como Usar

### Coleta de Cotações

Execute o arquivo principal:

```bash
python main.py
```

O sistema irá:
1. Buscar as cotações atuais de Dólar, Euro e Bitcoin
2. Inserir os dados no banco de dados SQLite
3. Adicionar os dados na planilha Excel (criando nova linha)
4. Calcular variações do dia atual
5. Exibir mensagens de confirmação

### Dashboard Interativo

Para visualizar o dashboard com gráficos e análises:

```bash
streamlit run view/dashboard.py
```

O dashboard exibe:
- Valores atuais das cotações com variações percentuais
- Gráfico de evolução temporal (linhas)
- Gráfico de variações diárias (barras)
- Médias móveis calculadas automaticamente

## Dados Coletados

Para cada execução, o sistema coleta:

| Campo      | Descrição                           |
|------------|-------------------------------------|
| data_hora  | Data e hora da coleta               |
| dolar      | Cotação do Dólar (USD → BRL)        |
| euro       | Cotação do Euro (EUR → BRL)         |
| bitcoin    | Cotação do Bitcoin (BTC → BRL)      |

## API Utilizada

**AwesomeAPI - Economia**
- Endpoint: `https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,BTC-BRL`
- Documentação: [https://docs.awesomeapi.com.br](https://docs.awesomeapi.com.br)

## Armazenamento

### Banco de Dados SQLite
- Arquivo: `data/database.db`
- Tabela: `cotacoes`
- Estrutura: id (PK), data_hora, dolar, euro, bitcoin

### Planilha Excel
- Arquivo: `data/cotacoes.xlsx`
- Formato: Cada linha representa uma coleta
- Atualização: Modo append (adiciona sem sobrescrever)

## Exemplos de Uso

### Coleta e armazenamento dos dados
```bash
python main.py
```

### Gerar Dashboard
```bash
streamlit run view/dashboard.py
```

### Execução periódica (Windows Task Scheduler)
Configure o Agendador de Tarefas do Windows para executar `main.py` em intervalos regulares.

### Execução periódica (Script)
Você pode criar um loop no código ou usar ferramentas como `schedule` para automatizar coletas.

## Observações

- Certifique-se de ter conexão com a internet para acessar a API
- O banco de dados e a planilha são criados automaticamente na primeira execução
- Dados anteriores são preservados - cada execução adiciona uma nova linha
- Logs de execução são salvos em `logs/app.log` (máximo 5MB, mantém 3 backups)

## Próximos Passos

Melhorias planejadas para versões futuras:

### Análise de Dados
- [x] Calcular variação percentual diária das cotações
- [x] Implementar médias móveis (7, 14, 30 dias)
- [ ] Comparação entre períodos (semanal, mensal)
- [ ] Identificar tendências de alta/baixa

### Visualização
- [x] Criar gráficos de linha mostrando evolução das cotações
- [x] Dashboard interativo com Streamlit ou Dash
- [x] Gráficos de correlação entre moedas
- [x] Indicadores visuais de variação

### Expansão de Dados
- [ ] Coletar dados históricos (últimos 30/90 dias)
- [ ] Adicionar mais moedas e criptomoedas
- [ ] Calcular indicadores técnicos (RSI, MACD)
- [ ] Incluir volume de negociação

### Automação e Robustez
- [x] Implementar coleta automática periódica (scheduler)
- [x] Sistema de logs de execução
- [x] Tratamento de erros (API fora do ar, sem internet)
- [x] Validação e sanitização de dados
- [ ] Testes unitários para funções principais

## Autor

Felipe Viana
