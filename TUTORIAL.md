# 📖 Guia de Operação — MLOps Challenge

Este tutorial explica como operar e testar a infraestrutura completa do desafio, incluindo o Gateway, Orquestração e Observabilidade.

---

## 🚀 1. Inicialização do Ambiente

O script principal para gerenciar o stack é o `start.sh`. Ele verifica o status dos containers e sobe apenas o que for necessário.

- **Iniciar tudo:**
  ```bash
  bash start.sh
  ```
- **Forçar recriação (reset):**
  ```bash
  bash start.sh --force
  ```

---

## 🛡️ 2. Gateway Nginx e Planos de Acesso

A infraestrutura separa o tráfego em dois planos distintos para maior segurança:

### 🔹 Plano de Inferência (Consumidores)
Usado para consumir as predições do modelo. Exige o header `X-API-Key`.

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

### 🔸 Plano de Controle (Automação/Pipeline)
Usado para disparar o pipeline de treinamento e deploy. Exige o header `X-Control-Key`.

**Disparar Pipeline:**
```bash
curl -X POST http://localhost:8080/webhook/d89ecb76-f1b5-4dd9-84bb-e6f085673962 \
     -H "X-Control-Key: super-secret-key"
```

---

## 🤖 3. Orquestração com n8n

O n8n é o cérebro do pipeline. Ele recebe o trigger e coordena as etapas.

1. **Acesso:** [http://localhost:5678](http://localhost:5678)
2. **Uso Local:** O arquivo `n8n/ml_pipeline.json` contém a definição completa do workflow. Você pode importá-lo localmente via *Workflows* -> *Import from File* para visualizar ou modificar a lógica de orquestração.
3. **Webhook:** O pipeline é disparado via gateway (ver exemplos de curl acima).

---

## 📊 4. Observabilidade (Grafana & Loki)

Todos os logs da API, do Gateway e do Pipeline são centralizados.

1. **Acesso:** [http://localhost:3000](http://localhost:3000)
2. **Credenciais:** `admin` / `admin`
3. **Visualizar Logs:**
   - Vá em **Explore**.
   - Selecione o datasource **Loki**.
   - Use o filtro para ver os logs da API: `{container="/mlops-challenge-api-1"}`
   - Use o filtro para o Worker do Pipeline: `{container="/mlops-challenge-worker-1"}`

---

## 📮 5. Testando com Postman

Para facilitar, utilize o arquivo `postman_collection.json`:

1. Importe a coleção no Postman.
2. A coleção já está dividida em pastas:
   - **Inference Plane:** Testes de predição e saúde.
   - **Control Plane:** Trigger para o pipeline completo.
3. As chaves de acesso já estão pré-configuradas nos headers das requisições.

---
