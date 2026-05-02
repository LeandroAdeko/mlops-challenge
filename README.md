# 🌐 MLOps Challenge Starter — Neural Machine Translation (EN → PT)

Repositório inicial (**starter kit**) para o desafio de MLOps. Contém as rotinas base de preparação de dados, treinamento e inferência para um modelo de tradução automática Inglês -> Português, utilizando um **Transformer** customizado com TensorFlow/Keras.

> **O objetivo do candidato é construir a automação end-to-end (CI/CD, orquestração, monitoramento, etc.) em cima destas rotinas já fornecidas.**
>
> 📄 **Consulte a especificação completa do desafio em [CHALLENGE.md](CHALLENGE.md).**

---

## 📋 Visão Geral

Este repositório fornece as **rotinas base** que o candidato utilizará para implementar a automação MLOps. As peças já inclusas são:

| Componente | Descrição |
|---|---|
| **Preparação de Dados** | Download e tokenização do dataset [ParaCrawl EN-PT](https://www.paracrawl.eu/) via TensorFlow Datasets, exportando TFRecords prontos para treino |
| **Treinamento** | Modelo Transformer (encoder-decoder) com warmup schedule, masked loss/accuracy e versionamento automático de artefatos |
| **Inference API** | API REST (FastAPI + Uvicorn) para tradução em tempo real, com métricas, health check e hot-reload de modelos |
| **Testes** | Suite de testes de contrato da API via Pytest + HTTPX |

> [!IMPORTANT]
> Estas rotinas já funcionam individualmente via Docker Compose. O desafio consiste em **automatizar e orquestrar** todo o ciclo de vida do modelo de ponta a ponta.

---

## 🏗️ Arquitetura

```
mlops_challenge_starter/
├── .github/                   # Workflows do GitHub Actions (CI/CD)
├── docs/                      # Diagramas da solução
├── pipeline/                  # Scripts e workers de execução do pipeline MLOps
├── nginx/                     # Configurações do Nginx API Gateway
├── n8n/                       # Definições de workflows de orquestração (n8n)
├── monitoring/                # Configurações de observabilidade (Grafana, Loki, Promtail)
├── ml/                        # Pipeline de ML
│   ├── common.py              # Utilitários (I/O JSON, hashing, run_id)
│   ├── tokenizers.py          # Download e carregamento de tokenizers
│   ├── prepare_dataset.py     # Preparação do dataset (TFRecords)
│   ├── model.py               # Transformer (Encoder/Decoder/Positional Encoding)
│   └── train.py               # Loop de treino, exportação de SavedModel
│
├── inference_api/             # API de inferência
│   ├── main.py                # Endpoints FastAPI
│   ├── model_manager.py       # Gerenciamento thread-safe do SavedModel
│   ├── schemas.py             # Schemas Pydantic (request/response)
│   ├── metrics.py             # Contadores de métricas da aplicação
│   └── logging_config.py      # Configuração de logging estruturado
│
├── tests/                     # Testes automatizados
│   └── test_api_contract.py   # Testes de contrato dos endpoints
│
├── data/                      # Dados processados (gerados)
├── artifacts/                 # Artefatos de treino (SavedModel, configs)
├── start.sh                   # Script principal de inicialização e verificação
├── postman_collection.json    # Coleção do Postman com chamadas de API configuradas
├── Dockerfile                 # Imagem base (Python 3.11-slim)
├── docker-compose.yml         # Orquestração de todos os serviços
└── requirements.txt           # Dependências Python
```

---

## 🧠 Modelo

O modelo é um **Transformer** com arquitetura encoder-decoder implementado do zero:

- **Positional Encoding** — codificação posicional sinusoidal
- **Encoder** — camadas com Multi-Head Attention + FFN + Layer Norm + Dropout
- **Decoder** — camadas com Self-Attention + Cross-Attention + FFN + Layer Norm
- **Learning Rate Schedule** — warmup linear seguido de decaimento inverso (baseado no paper *Attention Is All You Need*)

### Hiperparâmetros padrão

| Parâmetro | Valor |
|---|---|
| `num_layers` | 4 |
| `d_model` | 128 |
| `num_heads` | 4 |
| `dff` | 512 |
| `dropout` | 0.1 |
| `max_tokens` | 64 |

---

## 🛠️ Correções e Melhorias Realizadas (Resolução de Bugs)

Neste projeto, nos deparamos com erros estruturais que inviabilizavam a execução do fluxo base. Abaixo as correções aplicadas:

### 1. Ajuste de Versões de Bibliotecas e Conflitos (Protobuf e TensorFlow)
> **Problema**: Incompatibilidades e erros em tempo de execução causados por conflito de versões (ex: `AttributeError: 'FieldDescriptor' object has no attribute 'label'`).
- **Causa**: O ambiente de container precisava de um controle rigoroso nas dependências envolvendo TensorFlow e Protobuf.
- **Solução**: Foram definidas as versões específicas para as ferramentas de machine learning no `requirements.txt`: `tensorflow==2.18.1`, `tensorflow-text==2.18.1` e limitada a versão do `protobuf<5.0.0` para estabilizar o ambiente containerizado.

### 2. Falha de Dependência na API
> **Erro**: `import importlib-resources` (ModuleNotFoundError durante inicialização do app).
- **Causa**: Pacote ausente na imagem Docker de runtime.
- **Solução**: A dependência foi adicionada explicitamente no arquivo `requirements.txt`.

### 3. Falha Estrutural nos Testes (Pytest)
> **Erro**: `ModuleNotFoundError: No module named 'inference_api'`
- **Causa**: O `pytest` não conseguia mapear a pasta raiz como um pacote Python válido.
- **Solução**: Declaramos a variável de ambiente `PYTHONPATH: /workspace` nas configurações de teste no `docker-compose.yml`.

### 4. Inicialização de Modelos
> **Erro**: SavedModel não encontrado ao iniciar a API.
- **Causa**: O pathlib estava interpretando o `artifacts_dir` de forma incorreta.
- **Solução**: Removido o `.strip("/")` do `artifacts_dir` no arquivo `inference_api/model_manager.py`.

### 5. Exposição de Porta e Acesso no WSL 
- **Causa**: Nuances de conectividade na máquina host (WSL2).
- **Solução**: Mapeamento explícito das portas de serviço para permitir que o Postman no Windows acesse a API.

---

## 🚀 Solução Final e Como Executar

A infraestrutura agora engloba uma arquitetura MLOps completa, incluindo **Gateway**, **Orquestração de Pipeline** e **Observabilidade**.

### 1. Inicialização do Ambiente

O script principal para gerenciar o stack é o `start.sh`. Ele verifica o status dos containers e sobe apenas o que for necessário.

- **Iniciar tudo:**
  ```bash
  bash start.sh
  ```
- **Forçar recriação (reset):**
  ```bash
  bash start.sh --force
  ```

### 2. Gateway Nginx e Planos de Acesso

A infraestrutura separa o tráfego em dois planos distintos na porta `8080` para maior segurança:

#### 🔹 Plano de Inferência (Consumidores)
Usado para consumir as predições do modelo. Exige o header `X-API-Key: challenge-key`.

**Exemplo de Predição:**
```bash
curl -X POST http://localhost:8080/predict \
     -H "X-API-Key: challenge-key" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello world"}'
```

**Exemplo de Health Check:**
```bash
curl -X GET http://localhost:8080/health -H "X-API-Key: challenge-key"
```

#### 🔸 Plano de Controle (Automação/Pipeline)
Usado para disparar o pipeline de treinamento e deploy. Exige o header `X-Control-Key: super-secret-key`.

**Disparar Pipeline:**
```bash
curl -X POST http://localhost:8080/webhook/d89ecb76-f1b5-4dd9-84bb-e6f085673962 \
     -H "X-Control-Key: super-secret-key"
```

### 3. Orquestração com n8n

O n8n é o cérebro do pipeline. Ele recebe o trigger e coordena as etapas.
1. **Acesso:** [http://localhost:5678](http://localhost:5678)
2. **Uso Local:** O arquivo `n8n/ml_pipeline.json` contém a definição completa do workflow. Você pode importá-lo localmente via interface do n8n para visualizar.
3. **Webhook:** O pipeline é disparado via gateway na rota de controle especificada.

### 4. Observabilidade (Grafana & Loki)

Todos os logs da API, do Gateway e do Pipeline são centralizados.
1. **Acesso:** [http://localhost:3000](http://localhost:3000)
2. **Credenciais:** `admin` / `admin`
3. **Visualizar Logs:**
   - Vá em **Explore**.
   - Selecione o datasource **Loki**.
   - Use o filtro `{container="/mlops-challenge-api-1"}` para a API.
   - Use o filtro `{container="/mlops-challenge-worker-1"}` para o Worker.

### 5. Testando com Postman

Utilize o arquivo `postman_collection.json`:
1. Importe a coleção no Postman.
2. A coleção está dividida em **Inference Plane** e **Control Plane**.
3. As chaves de acesso já estão pré-configuradas nos headers das requisições.

---

## 🛠️ Stack Tecnológica

| Tecnologia | Uso |
|---|---|
| **Python 3.11** | Linguagem principal |
| **TensorFlow 2.18** | Framework de ML (modelo + servindo) |
| **TensorFlow Text 2.18** | Tokenização |
| **TensorFlow Datasets** | Download do dataset ParaCrawl |
| **FastAPI** | Framework da API REST |
| **Uvicorn** | Servidor ASGI |
| **Nginx** | API Gateway (Rate Limiting e Autenticação) |
| **n8n** | Orquestração de Pipeline MLOps |
| **Grafana + Loki + Promtail** | Stack de Observabilidade e Logs |
| **Docker / Docker Compose** | Containerização e orquestração |