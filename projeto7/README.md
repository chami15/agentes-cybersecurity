# Projeto 7 — Vulnerability Triage AI

Pipeline **autônomo de pentest defensivo** com 5 nós em LangGraph: escaneia uma porta, valida credenciais fracas, re-ranqueia vulnerabilidades por risco de negócio, gera comandos de remediação e produz um relatório final em `.docx`.

## O que faz

O alvo padrão é o `vulnerable-db` provisionado pelo `docker-compose` (MySQL 5.7 com senha root `123456`). O grafo executa:

1. **Scanner Node** — Tool `port_scan_tool` (socket TCP) verifica se a porta está aberta. Se `CLOSED`, o roteador condicional encerra o processo.
2. **Triage Node** — Se for MySQL, roda `mysql_login_check` (força bruta controlada com wordlist pequena: `root`, `123456`, `password`, `admin`). Se acertar, registra "Weak Credentials (CRITICAL)" e roda `safe_sql_query` (`SELECT @@version`) para detectar versão desatualizada.
3. **Rerank Node** — Um LLM (`llama3` via Ollama) recebe a lista de vulnerabilidades e atribui um score 0-100 de risco de negócio (CISO mindset).
4. **Remediation Node** — Gera os comandos técnicos exatos de correção (SQL/Bash) para cada vulnerabilidade, contextualizados para MySQL 5.7 + Docker.
5. **Reporter Node** — Compila tudo em um relatório de pentest profissional em português (Executive Summary, Technical Findings, Remediation), com modelo `mistral`.

A saída é convertida em `.docx` com `python-docx` (`Relatorio_final_pentest.docx`).

## Quando usar

Use este projeto como referência quando precisar de:
- Um exemplo **completo de LangGraph com roteamento condicional** (`add_conditional_edges`) — o fluxo aborta cedo se a porta estiver fechada, evitando trabalho desperdiçado.
- Padrão de **guardrails em tools de SQL** — `sql_safety_guardrail` bloqueia `DROP/DELETE/TRUNCATE/ALTER/GRANT/FLUSH` antes de executar, ilustrando como dar autonomia controlada ao agente.
- Uso de **dois LLMs com responsabilidades diferentes**: `mistral` (rápido) para o relatório final, `llama3` (mais capaz) para reranking e remediação.
- Geração de **artefato final em formato corporativo** (`.docx`) com formatação heurística de markdown → docx via `python-docx`.
- Ambiente vulnerável **dockerizado** (MySQL 5.7 com senha fraca) para experimentar sem risco.

## Stack

- **LangGraph** com `StateGraph` + `add_conditional_edges`.
- **Ollama** (`mistral` + `llama3`) via `langchain-ollama`.
- **mysql-connector-python** + **socket** para as tools de scan e validação.
- **python-docx** para gerar o relatório final.
- **Docker Compose** com MySQL 5.7 vulnerável.

## Estrutura

- [main.py](main.py) — Define o grafo, o roteador condicional, executa o pipeline e gera o `.docx`.
- [nodes.py](nodes.py) — Os 5 nós: scanner, triage, rerank, remediation, reporter.
- [tools.py](tools.py) — Tools de pentest (`port_scan_tool`, `mysql_login_check`, `safe_sql_query`) e o guardrail SQL.
- [state.py](state.py) — `AgentState` (TypedDict) com os campos do estado compartilhado.
- [docker-compose.yml](docker-compose.yml) — MySQL 5.7 com senha fraca para testes.
- [Relatorio_final_pentest.docx](Relatorio_final_pentest.docx) — Saída de exemplo da última execução.

## Como rodar

1. Instale e inicie o Ollama: `ollama pull mistral && ollama pull llama3`.
2. Suba o banco vulnerável: `docker-compose up -d`.
3. Instale dependências: `pip install -r requirements.txt`.
4. Execute: `python main.py`.
5. O relatório final aparece no terminal e é salvo como `Relatorio_final_pentest.docx`.
