#!/bin/bash

# Parse flags
FORCE=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -f|--force) FORCE=true ;;
        *) echo "Parâmetro desconhecido: $1"; exit 1 ;;
    esac
    shift
done

echo "Iniciando a infraestrutura do MLOps Challenge..."

# Lista de serviços principais para verificar
SERVICES=("api" "gateway" "loki" "promtail" "grafana" "n8n")
NEEDS_UP=false
MISSING_SERVICES=()

if [ "$FORCE" = true ]; then
    echo "Modo --force ativado. Forçando a recriação dos containers..."
    NEEDS_UP=true
    UP_FLAGS="--force-recreate"
else
    echo "Verificando o status dos serviços..."
    for SERVICE in "${SERVICES[@]}"; do
        # Verifica se o serviço está rodando
        STATUS=$(docker compose ps "$SERVICE" --status running --format "{{.Service}}" 2>/dev/null)
        if [ -z "$STATUS" ]; then
            MISSING_SERVICES+=("$SERVICE")
            NEEDS_UP=true
        fi
    done
    UP_FLAGS=""
fi

if [ "$NEEDS_UP" = true ]; then
    if [ "$FORCE" = false ]; then
        echo "Serviços fora do ar: ${MISSING_SERVICES[*]}"
    fi
    echo "Subindo os serviços principais (API, Nginx, Observabilidade, n8n)..."
    docker compose --profile api up -d $UP_FLAGS
else
    echo "✅ Todos os serviços já estão em execução."
    echo "Dica: Use --force ou -f para forçar a atualização dos containers."
fi

echo ""
echo "Resumo da infraestrutura:"
echo "--------------------------------------------------------"
echo "Gateway (Nginx):  http://localhost:8080"
echo "Grafana:          http://localhost:3000 (admin/admin)"
echo "n8n:             http://localhost:5678"
echo "--------------------------------------------------------"
echo "Para acompanhar os logs no Grafana:"
echo "   1. Acesse http://localhost:3000"
echo "   2. Vá em 'Explore' e selecione o datasource 'Loki'"
echo "   3. Filtro sugerido para API: {container=\"/mlops-challenge-api-1\"}"
echo ""
echo "Treinamento de modelo (em outro terminal):"
echo "   docker compose --profile train up"

