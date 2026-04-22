import asyncio
import zmq
import zmq.asyncio
import random
import datetime
import json

PORT = 5555

context = zmq.asyncio.Context()

socket = context.socket(zmq.PUB)

socket.bind(f'tcp://*:{PORT}')

SCENARIOS = [

    {"source": "AWS-GuardDuty", "log": "Bucket S3 'dados-financeiros' é acessível publicamente através de ACL."},

    {"source": "App-WAF", "log": "Detectado payload 'OR 1=1' no campo de login fornecido por IP 192.168.1.5."},

    {"source": "CI-Pipeline", "log": "A dependência 'requests' versão 2.18.0 tem sido conhecida pela vulnerabilidade CVE-2023-XXXX."},
    
    {"source": "K8s-Audit", "log": "Pod 'payment-service' começou com o contexto privileged=true."},

    {"source": "System", "log": "O usuário 'admin' fez login com sucesso a partir de um IP conhecido.."},

    {"source": "Git-Scanner", "log": "ID da chave de acesso da AWS encontrada no arquivo de histórico de commits 'config.py'."}
]

async def generate_logs():
    print(f'Iniciando a publicação dos logs na porta {PORT}')

    while True:
        await asyncio.sleep(random.uniform(2,5))

        scenario = random.choice(SCENARIOS)

        event = {
            'type' : 'LOG',
            'timestamp' : datetime.datetime.now().strftime("%H:%M:%S"),
            'source' : scenario['source'],
            'raw_log' : scenario['log']
        }

        print(f'Enviando log: {scenario["source"]}')

        await socket.send_json(event)

if __name__ == '__main__':
    try: 
        asyncio.run(generate_logs())

    except KeyboardInterrupt:
        print('Producer encerrado')

        