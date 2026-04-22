# Projeto 6 — AgenteOps / DevSecOps (event-driven)

Pipeline de segurança **event-driven em tempo real**: um produtor publica logs simulados em um barramento ZeroMQ, um motor de IA classifica cada evento e propõe correções, e um dashboard CLI exibe tudo em tempo real.

## O que faz

Três processos rodam em paralelo, conectados via ZeroMQ pub/sub:

1. **Producer** ([producer.py](producer.py)) — Publica eventos JSON aleatórios na porta 5555 a cada 2-5s, simulando alertas de AWS GuardDuty, WAF, K8s Audit, CI Pipeline e Git Scanner.
2. **Engine** ([engine.py](engine.py)) — Assina os logs do producer. Para cada evento, roda dois agentes:
   - **Agente Triagem** — Classifica via Ollama (`llama3`) com saída JSON validada por Pydantic: `is_threat`, `severity` (LOW/MEDIUM/HIGH/CRITICAL), `category`, `reasoning`.
   - **Agente Remediation** — Se a severidade ≥ MEDIUM (ou for S3/Key), gera o comando técnico de correção (CLI AWS, YAML K8s, código parametrizado). Publica o pacote enriquecido na porta 5556.
3. **Dashboard** ([dashboard.py](dashboard.py)) — UI rica em terminal (`rich`) com três painéis: stream de logs, ameaças detectadas com reasoning da IA, e plano de ação sugerido (com código).

## Quando usar

Use este projeto como referência quando precisar de:
- Uma **arquitetura desacoplada via pub/sub** (ZeroMQ) — cada componente roda independente, pode ser escalado e reiniciado sem afetar os outros. Útil para SOC/observabilidade em tempo real.
- Um exemplo **100% local** com Ollama (sem custo de API, sem dados saindo da máquina) — bom para ambientes air-gapped ou demos offline.
- Padrão de **saída estruturada validada por Pydantic** com `JsonOutputParser` do LangChain — garante que o agente sempre devolve JSON parseável.
- Dashboard CLI rico com `rich.live` — alternativa leve ao Streamlit/web quando você quer monitoramento em terminal.
- Pipeline **assíncrono** (`asyncio` + `zmq.asyncio`) processando eventos sem bloquear.

## Stack

- **ZeroMQ** (`pyzmq`) — barramento pub/sub.
- **Ollama** (`llama3` local) via `langchain-ollama`.
- **Pydantic** + `JsonOutputParser` para schemas das saídas.
- **rich** para o dashboard de terminal.
- **asyncio** end-to-end.

## Estrutura

- [producer.py](producer.py) — Gerador de eventos sintéticos.
- [engine.py](engine.py) — Motor de IA com dois agentes (triagem + remediação) e os schemas Pydantic.
- [dashboard.py](dashboard.py) — UI de terminal com `rich`.
- [requirements.txt](requirements.txt) — Dependências.

## Como rodar

1. Instale e inicie o Ollama com o modelo `llama3`: `ollama pull llama3`.
2. Instale dependências: `pip install -r requirements.txt`.
3. Em três terminais separados (nesta ordem):
   - `python engine.py`
   - `python dashboard.py`
   - `python producer.py`
4. Observe o dashboard recebendo logs, classificando ameaças e propondo fixes em tempo real.
