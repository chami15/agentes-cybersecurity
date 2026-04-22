import os
import json
from openai import OpenAI
from logsense_ia import search_logs, block_ip_firewall
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def agente_seguranca_autonomo():
    print('Inicializando o Agente')
    topico_ataque = 'Tentativa de ataque, sql injection ou login falho'
    print(f'\n1. Buscando topico de ataque {topico_ataque}')

    contexto_log = search_logs(topico_ataque, n_results=5)

    print('Logs recuperados enviando para o Agente')

    prompt_sistema = """
    Você é um Analista de Segurança Sênior Autônomo (Cybersecurity Agent).
    Sua tarefa é analisar logs de servidor e decidir se uma ação defensiva é necessária.
    
    REGRAS DE DECISÃO:
    1. Se identificar um ataque claro (SQL Injection, Brute Force confirmado, etc.) com um IP de origem, você DEVE ordenar o bloqueio.
    2. Se forem apenas erros comuns ou sem IP de origem claro, ordene apenas MONITORAR.
    
    FORMATO DE RESPOSTA OBRIGATÓRIO (JSON):
    {
        "analise": "Breve explicação do que você encontrou",
        "decisao": "BLOQUEAR" ou "MONITORAR",
        "ip_alvo": "IP para bloquear (ou null se não houver)",
        "motivo_bloqueio": "Explicação curta para o firewall"
    }
    """

    prompt_usuario = f""" 
    Aqui estão os logs recuperados do sistema:
    {contexto_log}
    Qual é a sua decisão? Responda apenas em JSON
    """

    print('Analisando padrões de ataque e decidindo operação.')

    try:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system','content': prompt_sistema},
                {'role': 'user','content': prompt_usuario}
            ],
            response_format={'type': 'json_object'},
            temperature=0.0
        )

        resultado_llm = response.choices[0].message.content
        decisao_json = json.loads(resultado_llm)

        print(f'Analise do agente: {decisao_json["analise"]}')
        print(f'Decisão do agente: {decisao_json["decisao"]}')

        print('Agente agindo...')

        if decisao_json['decisao'] == 'BLOQUEAR' and decisao_json['ip_alvo']:
            print(f'Ameaça critica detectada iniciando bloqueio de {decisao_json["ip_alvo"]}')

            resultado_acao = block_ip_firewall(ip_adress=decisao_json['ip_alvo'], reason=decisao_json['motivo_bloqueio'])

            print(f'Resultado da ação: {resultado_acao}')

        else:
            print('Nenhuma ação necessária')

    except Exception as e:
        print(f'Erro do raciocinio do agente: {e}')

if __name__ == '__main__':
    agente_seguranca_autonomo()


