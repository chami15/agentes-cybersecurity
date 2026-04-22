# Projeto 3 — LogSense AI (MCP)

Servidor **MCP (Model Context Protocol)** que indexa logs de servidor em um vector store e expõe ferramentas de busca semântica e ação defensiva. Acompanha três versões evolutivas de cliente que consomem essas tools — desde uma chamada manual até um agente autônomo que decide sozinho quando bloquear um IP.

## O que faz

[logsense_ia.py](logsense_ia.py) é um servidor MCP construído com `FastMCP` que:
- Lê `server_logs.txt` e gera embeddings com OpenAI (`text-embedding-3-small`).
- Armazena tudo em uma collection ChromaDB em memória.
- Expõe três tools MCP: `search_logs` (busca semântica), `get_log_statistics` e `block_ip_firewall` (ação defensiva simulada).

Os três scripts `executa_agente_v*.py` mostram a evolução de uso dessas tools:

- **v1** — Pipeline simples: ingestão + estatísticas + uma busca semântica direta. Sem LLM, sem decisão.
- **v2** — Compõe duas tools sequencialmente: faz uma busca e força um bloqueio em um IP fixo.
- **v3** — Agente **autônomo** com `gpt-4o-mini`: recebe os logs recuperados, decide via JSON estruturado se é caso de `BLOQUEAR` ou `MONITORAR`, e — se for bloquear — chama a tool de firewall com o IP que ele mesmo extraiu.

## Quando usar

Use este projeto como referência quando precisar de:
- Um exemplo mínimo de **servidor MCP** em Python com `FastMCP` expondo tools customizadas.
- Comparar três níveis de "autonomia" de IA aplicados ao mesmo conjunto de tools:
  1. **Pipeline determinístico** (v1) — útil quando o fluxo é fixo.
  2. **Composição de tools sem LLM no loop** (v2) — útil quando a lógica é simples.
  3. **Agente com tool-calling estruturado via JSON** (v3) — útil quando a decisão depende de análise contextual.
- Padrão de **resposta JSON forçada** com `response_format={'type': 'json_object'}` da OpenAI para decisões de agentes confiáveis.

## Stack

- **MCP** (`mcp.server.fastmcp.FastMCP`) para expor tools.
- **OpenAI** (`gpt-4o-mini` no v3, `text-embedding-3-small` para embeddings).
- **ChromaDB** em memória.

## Estrutura

- [logsense_ia.py](logsense_ia.py) — Servidor MCP, ingestão de logs e definição das tools.
- [executa_agente_v1.py](executa_agente_v1.py) — Cliente determinístico (busca direta).
- [executa_agente_v2.py](executa_agente_v2.py) — Cliente que encadeia tools manualmente.
- [executa_agente_v3.py](executa_agente_v3.py) — Agente autônomo com decisão via LLM.
- [server_logs.txt](server_logs.txt) — Logs de exemplo para indexação.
- `.env` — Espera `OPENAI_API_KEY`.

## Como rodar

1. Configure `OPENAI_API_KEY` no `.env`.
2. Instale dependências: `pip install -r requirements.txt`.
3. Execute qualquer cliente: `python executa_agente_v3.py` (recomendado para ver o agente decidindo).
4. Para rodar o servidor MCP standalone: `python logsense_ia.py`.
