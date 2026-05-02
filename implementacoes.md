# Resumo de Correções (MLOps Challenge)

Neste documento, consolidamos as correções e melhorias estruturais realizadas no projeto base.

## Resolução de Bugs e Melhorias de Deploy

Durante a execução do projeto, nos deparamos com erros estruturais que inviabilizavam a execução do fluxo. Abaixo as correções aplicadas:

### 1. Ajuste de Versões de Bibliotecas e Conflitos (Protobuf e TensorFlow)
> **Problema**: Incompatibilidades e erros em tempo de execução causados por conflito de versões (ex: `AttributeError: 'FieldDescriptor' object has no attribute 'label'`).
- **Causa**: O ambiente de container precisava de um controle rigoroso nas dependências envolvendo TensorFlow e Protobuf.
- **Solução**: Foram definidas as versões específicas para as ferramentas de machine learning no `requirements.txt`: `tensorflow==2.18.1`, `tensorflow-text==2.18.1` e limitada a versão do `protobuf<5.0.0` para estabilizar o ambiente containerizado, resolvendo os problemas na preparação de dados e treinamento.

### 2. Falha de Dependência na API
> **Erro**: `import importlib-resources` (ModuleNotFoundError durante inicialização do app).
- **Causa**: Alguma biblioteca da nossa pipeline de inferência demandava esse pacote, que estava ausente na imagem Docker de runtime.
- **Solução**: A dependência foi adicionada explicitamente no arquivo `requirements.txt`. Com o rebuild do container, o pacote é instalado corretamente, normalizando o boot do `uvicorn`.

### 3. Falha Estrutural nos Testes (Pytest)
> **Erro**: `ModuleNotFoundError: No module named 'inference_api'`
- **Causa**: Ao rodar o profile de `tests` no Docker Compose, o `pytest` não conseguia mapear a pasta raiz (`/workspace`) como um pacote Python válido, não encontrando o módulo principal de inferência do sistema.
- **Solução**: Resolvemos o problema a nível de container, declarando a variável de ambiente `PYTHONPATH: /workspace` nas configurações de teste no `docker-compose.yml`. Com isso, o Python passa a compreender que a raiz também faz parte das rotas de pacotes locais.

### 4. Inicialização de Modelos
> **Erro**: SavedModel não encontrado: `workspace/artifacts/nmt_20260501T020331Z_uqevf5/saved_model`
- **Causa/Contexto**: Ao inicializar a API, o modelo não era carregado. O pathlib estava interpretando o `artifacts_dir` de forma incorreta.
- **Solução**: Removido o `.strip("/")` do `artifacts_dir` no arquivo `inference_api/model_manager.py`.

### 5. Exposição de Porta e Acesso no WSL 
- **Causa/Contexto**: Devido a nuances de conectividade na máquina do host, o acesso à API em ambientes com WSL2 requer binds apropriados.
- **Solução**: Mapeamento explícito das portas de serviço, garantindo repasse correto e tornando o Postman na máquina Windows capaz de consumir a API da rede Docker.

---
**Conclusão**: O ambiente base agora está corrigido, com as dependências alinhadas (Protobuf, TensorFlow, importlib-resources, etc.) e livre dos gargalos que bloqueavam o ciclo de desenvolvimento.
