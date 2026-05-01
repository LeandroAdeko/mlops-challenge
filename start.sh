#!/bin/bash

echo "Iniciando a infraestrutura do MLOps Challenge..."


# Sobe a stack principal em modo detached (segundo plano)
echo "Subindo os serviços principais (API, Nginx, Observabilidade, n8n)..."
docker compose --profile api up -d --force-recreate

echo ""
echo "Todos os serviços principais estão no ar!"
echo "--------------------------------------------------------"
echo "Gateway (Nginx):  http://localhost:8080"
echo "Grafana:          http://localhost:3000 (admin/admin)"
echo "n8n:             http://localhost:5678"
echo "--------------------------------------------------------"
echo "Para acompanhar e filtrar os logs em tempo real, acesse o Grafana:"
echo "   1. Abra http://localhost:3000"
echo "   2. Vá na aba 'Explore' e garanta que a fonte de dados seja o Loki"
echo "   3. Exemplo de busca para ver os logs da API: {container=\"/mlops-challenge-api-1\"}"
echo ""
echo "Para rodar o treinamento de um novo modelo, execute em outro terminal:"
echo "   docker compose --profile train up"
