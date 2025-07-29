# FIDI Common Libraries

Bibliotecas compartilhadas entre os projetos da FIDI, desenvolvidas seguindo as melhores práticas de desenvolvimento Python.

## 📋 Visão Geral

Este projeto fornece um conjunto de bibliotecas reutilizáveis para automação, integração AWS, processamento de dados e utilitários comuns utilizados nos projetos da FIDI.

## 🚀 Funcionalidades Principais

- **Data**: Operações de banco de dados multi-SGBD (Oracle, PostgreSQL, SQL Server)
- **Utils**: Sistema de logging estruturado para múltiplos SGBDs
- **Constants**: Constantes de status padronizadas e funções de conversão entre diferentes tipos de status
- **AWS**: Clientes padronizados para SQS, SNS, Lambda, S3 com configuração centralizada
- **Config**: Gerenciamento de parâmetros com cache e conversão automática de tipos
- **UI**: Componentes para automação de interfaces gráficas (em desenvolvimento)

## 📦 Instalação e Configuração

### Pré-requisitos
- Python 3.9+
- Poetry

### Instalação como Biblioteca
```bash
# Instalar via Poetry (recomendado)
poetry add git+https://github.com/your-org/fidi-common-libraries.git

# Ou via pip
pip install git+https://github.com/your-org/fidi-common-libraries.git
```

### Desenvolvimento Local
```bash
# Clone o repositório
git clone <repository-url>
cd fidi-common-libraries

# Instale as dependências
poetry install

# Ative o ambiente virtual
poetry shell
```

### Configuração de Desenvolvimento
```bash
# Instale os hooks de pre-commit
poetry run pre-commit install

# Execute os testes
poetry run pytest

# Verifique a cobertura de testes
poetry run pytest --cov=src --cov-report=html
```

## 🔧 Como Usar

### Módulo Data - Operações de Banco

```python
from fidi_common_libraries.data.db_data import DatabaseConfig, ProcessosRpaInserter, DatabaseQuery
from datetime import datetime

# Configuração do banco
db_config = DatabaseConfig.from_env('RPA_')  # Usa variáveis RPA_DB_SERVER, etc.

# Inserir registro
inserter = ProcessosRpaInserter(db_config)
registro_id = inserter.insert(
    ambiente="PRD",
    produto="FIDI-ferias",
    versao="1.0.0",
    chapa="123456",
    statusexecucao="NOVO"
)

# Consulta segura
query = DatabaseQuery(db_config)
results = query.execute_query(
    "SELECT * FROM processosrpa WHERE statusexecucao = :status",
    {"status": "NOVO"}
)
```

### Módulo Config - Gerenciamento de Parâmetros

```python
from fidi_common_libraries.config.parametros import Parametros

# Inicializar o gerenciador de parâmetros
params = Parametros(ambiente="HML", produto="FIDI-ferias")

# Obter um parâmetro
url_api = params.get_parametro("URL_API", default="https://api.exemplo.com")

# Obter parâmetros por grupo
config_email = params.get_parametros_por_grupo("Email")

# Obter parâmetros por categorias específicas
config_ti = params.get_parametros_por_grupo("TI")  # Configurações técnicas
config_negocio = params.get_parametros_por_grupo("Negocio")  # Configurações de negócio
config_produto = params.get_parametros_por_grupo("Produto")  # Configurações do produto

# Atualizar um parâmetro
params.atualizar_parametro("TIMEOUT_API", 30)
```

### Módulo Utils - Logging e Status

```python
from fidi_common_libraries.utils.logger import registrar_log_banco
from fidi_common_libraries.constants.status import HubStatus, DBStatus, LogStatus, convert_status
import pyodbc

# Conexão com banco
conn = pyodbc.connect(connection_string)

# Registrar log (detecta automaticamente o tipo de banco)
registrar_log_banco(
    conn=conn,
    ambiente="PRD",
    produto="FIDI-ferias",
    versao="1.0.0",
    nivel="INFO",
    modulo="main",
    processo="processamento",
    acao="inicio",
    lote="LOTE001",
    mensagem="Processo iniciado",
    usuario="sistema",
    status_execucao=LogStatus.SUCESSO,
    hostname="server01",
    ip_origem="192.168.1.100"
)

# Usar constantes de status
status_db = DBStatus.NOVO
status_log = convert_status(status_db, 'db', 'log')
```

### Módulo AWS - Clientes Padronizados

```python
from fidi_common_libraries.aws.common_aws import AWSClientFactory, AWSConfig, create_message_with_metadata

# Configuração AWS
config = AWSConfig.from_env()  # Usa variáveis AWS_REGION, AWS_ACCESS_KEY_ID, etc.
factory = AWSClientFactory(config)

# Cliente SQS
sqs = factory.get_sqs_client()
message_id = sqs.send_message(
    queue_url="https://sqs.sa-east-1.amazonaws.com/123456789/my-queue",
    message={"data": "test"},
    message_attributes={"Type": {"StringValue": "ProcessData", "DataType": "String"}}
)

# Cliente SNS
sns = factory.get_sns_client()
sns.publish_message(
    topic_arn="arn:aws:sns:sa-east-1:123456789:my-topic",
    message=create_message_with_metadata({"event": "process_completed"}),
    subject="Processo Finalizado"
)

# Cliente Lambda
lambda_client = factory.get_lambda_client()
result = lambda_client.invoke_function(
    function_name="my-function",
    payload={"action": "process", "data": "test"}
)

# Cliente S3
s3 = factory.get_s3_client()
s3.upload_file("/path/to/file.txt", "my-bucket", "uploads/file.txt")
```

## 🏗️ Estrutura do Projeto

```
fidi-common-libraries/
├── src/
│   └── fidi_common_libraries/
│       ├── aws/          # Utilitários AWS
│       ├── config/       # Gerenciamento de configurações e parâmetros
│       ├── constants/    # Constantes e enums compartilhados
│       ├── data/         # Processamento de dados e acesso a banco
│       ├── ui/           # Automação de UI
│       └── utils/        # Utilitários gerais e logging
├── tests/
│   ├── unit/            # Testes unitários
│   ├── integration/     # Testes de integração
│   └── e2e/            # Testes end-to-end
├── docs/               # Documentação
├── scripts/            # Scripts auxiliares
└── resources/          # Recursos estáticos
```

## 🧪 Testes

O projeto mantém uma cobertura de testes superior a 85%:

```bash
# Executar todos os testes
poetry run pytest

# Executar com cobertura
poetry run pytest --cov=src --cov-report=term-missing

# Executar apenas testes unitários
poetry run pytest tests/unit/
```

## 📊 Qualidade de Código

Ferramentas utilizadas:
- **Black**: Formatação automática
- **Flake8**: Linting
- **MyPy**: Verificação de tipos
- **Bandit**: Análise de segurança

```bash
# Formatação
poetry run black src/ tests/

# Linting
poetry run flake8 src/ tests/

# Verificação de tipos
poetry run mypy src/

# Análise de segurança
poetry run bandit -r src/
```

## 📚 Documentação

- [INSTALL.md](INSTALL.md) - Guia completo de instalação e uso
- [CHANGELOG.md](CHANGELOG.md) - Histórico de mudanças
- [STATUS_ATUAL.md](STATUS_ATUAL.md) - Estado atual do projeto
- [src/fidi_common_libraries/config/ScriptsDB_Datametria_Parametros.sql](src/fidi_common_libraries/config/ScriptsDB_Datametria_Parametros.sql) - Script SQL para criação dos objetos de banco de dados para parâmetros

## 🤝 Contribuição

1. Siga as diretrizes estabelecidas em `.amazonq/rules/`
2. Mantenha a cobertura de testes acima de 85%
3. Execute os pre-commit hooks antes de fazer commit
4. Atualize a documentação conforme necessário

## 📄 Licença

Este projeto está licenciado sob os termos definidos no arquivo [LICENSE](LICENSE).