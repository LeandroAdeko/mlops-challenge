from __future__ import annotations

import json
import logging
import os
import subprocess
import sys

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("pipeline-worker")

app = FastAPI(title="MLOps Pipeline Worker")

# Configurações via variáveis de ambiente
ARTIFACTS_DIR = os.getenv("ARTIFACTS_DIR")
DATA_DIR = os.getenv("DATA_DIR")
API_URL = os.getenv("API_URL")

class TrainParams(BaseModel):
    epochs: int = 10
    batch_size: int = 32
    threshold: float = 0.30
    git_sha: str = "unknown"

class PrepareParams(BaseModel):
    dataset_name: str = "para_crawl/enpt"
    max_tokens: int = 64
    train_records: int = 20000
    val_records: int = 2000


@app.post("/run/prepare")
def run_prepare(params: PrepareParams = PrepareParams()):
    logger.info("Iniciando preparação de dados...")
    cmd = [
        "python", "-m", "ml.prepare_dataset",
        "--output_dir", str(DATA_DIR),
        "--dataset_name", str(params.dataset_name),
        "--max_tokens", str(params.max_tokens),
        "--train_records", str(params.train_records),
        "--val_records", str(params.val_records)
    ]
    logger.debug(f"Comando de preparação: {cmd}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        for line in result.stdout.splitlines():
            logger.info(line)
        if result.stderr:
            for line in result.stderr.splitlines():
                logger.error(line)
                
        logger.info("Preparação concluída com sucesso.")
        # Tenta encontrar a última linha de JSON na saída
        output_json = None
        for line in reversed(result.stdout.splitlines()):
            if line.strip().startswith("{"):
                try:
                    output_json = json.loads(line)
                    break
                except Exception as e:
                    logger.error(f"Erro ao parsear JSON: {e}")
                    continue
        return {"status": "success", "output": output_json or result.stdout}
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro na preparação: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Prepare failed: {e.stderr}")

@app.post("/run/train")
def run_train(params: TrainParams = TrainParams()):
    logger.info("Iniciando treinamento do modelo...")
    cmd = [
        "python", "-m", "ml.train",
        "--data_dir", str(DATA_DIR),
        "--artifacts_dir", str(ARTIFACTS_DIR),
        "--epochs", str(params.epochs),
        "--batch_size", str(params.batch_size),
        "--threshold", str(params.threshold),
        "--git_sha", str(params.git_sha)
    ]
    logger.debug(f"Comando de treinamento: {cmd}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        for line in result.stdout.splitlines():
            logger.info(line)
        if result.stderr:
            for line in result.stderr.splitlines():
                logger.error(line)
                
        logger.info("Treinamento concluído.")
        
        # O train.py imprime um resumo JSON no final
        summary = None
        for line in reversed(result.stdout.splitlines()):
            if line.strip().startswith("{"):
                try:
                    summary = json.loads(line)
                    break
                except Exception as e:
                    logger.error(f"Erro ao parsear JSON: {e}")
                    continue
        
        if not summary:
             return {"status": "success", "raw_output": result.stdout}
             
        return summary
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro no treinamento: {e.stderr}")
        raise HTTPException(status_code=500, detail=f"Train failed: {e.stderr}")

class DeployRequest(BaseModel):
    run_id: str

@app.post("/run/deploy")
async def run_deploy(req: DeployRequest):
    logger.info(f"Solicitando deploy do modelo: {req.run_id}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_URL}/reload",
                json={"run_id": req.run_id},
                headers={"X-API-Key": os.getenv("API_KEY", "challenge-key")},
                timeout=30.0
            )
            response.raise_for_status()
            logger.info(f"Deploy concluído: {response.json()}")
            return response.json()
        except Exception as e:
            logger.error(f"Erro no deploy: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Deploy failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
