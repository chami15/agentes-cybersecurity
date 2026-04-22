# Projeto 5 — IncidentOps (Detective + Responder)

Sistema **multi-agente** que escaneia um banco PostgreSQL em busca de permissões inseguras concedidas a `PUBLIC`, decide se é incidente, gera o comando SQL de contenção e — após confirmação humana — executa a correção no banco.

## O que faz

O ambiente é provisionado via `docker-compose`: um Postgres "vulnerável" sobe com uma tabela `salarios_confidenciais` que tem `GRANT ALL ... TO PUBLIC` (a vulnerabilidade plantada). O fluxo do agente:

1. **Tool `inspect_permission`** — Faz um `SELECT` em `information_schema.role_table_grants` filtrando por `grantee = 'PUBLIC'` e devolve um relatório textual.
2. **Agente Detetive** — Recebe o relatório bruto e devolve um JSON estruturado: `{is_incident, severity, summary}`.
3. Se `is_incident = true`, o **Agente Respondente** gera o comando SQL exato de `REVOKE` (sem markdown, sem explicação — só o SQL).
4. **Human-in-the-loop** — O sistema pede confirmação via `input()` antes de executar. Se o usuário confirma, a tool `execute_contaiment` roda o `REVOKE` e revalida o ambiente.

## Quando usar

Use este projeto como referência quando precisar de:
- Um exemplo de **dois agentes especializados em série** (analisar → propor ação) sem framework de grafo — apenas chains LangChain encadeadas manualmente, útil para ver o "esqueleto" sem a abstração do LangGraph.
- Demonstrar **JSON estruturado como contrato** entre agentes (o detetive devolve JSON; a decisão de seguir ou não é feita por código Python lendo esse JSON).
- Padrão **human-in-the-loop** antes de executar ações destrutivas (o agente sugere, o humano aprova).
- Setup de **ambiente vulnerável reproduzível** com Docker para testar agentes de segurança defensiva.

## Stack

- **LangChain + Groq** (`llama-3.3-70b-versatile`) para os dois agentes (sem LangGraph).
- **psycopg2** para acessar o Postgres.
- **Docker Compose** + **Postgres 18** com `init.sql` que planta a vulnerabilidade.

## Estrutura

- [main.py](main.py) — Orquestração: chama as tools, define os prompts dos dois agentes e gerencia a confirmação do usuário.
- [tools.py](tools.py) — `tool_inspect_permission` (scan de permissões) e `tool_execute_contaiment` (executa SQL de contenção).
- [docker-compose.yml](docker-compose.yml) — Postgres com volume montando o `init.sql`.
- [init.sql](init.sql) — Cria a tabela sensível e concede `ALL PRIVILEGES` ao `PUBLIC` (a vulnerabilidade).
- `.env` — Espera `GROQ_API_KEY`, `DB_NAME`, `DB_USER`, `DB_PASS`, `DB_HOST`, `DB_PORT`.

## Como rodar

1. Configure o `.env` com as credenciais do banco e a `GROQ_API_KEY`.
2. Suba o banco: `docker-compose up -d`.
3. Execute: `python main.py`.
4. Quando o agente sugerir o comando de contenção, digite `s` para executar.
