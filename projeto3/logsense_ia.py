import os 
import datetime
import chromadb
from chromadb.utils import embedding_functions 
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
load_dotenv()

LOG_FILE = 'server_logs.txt'

mcp = FastMCP('LogSense AI')

openai_eb = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv('OPENAI_API_KEY'),
    model_name='text-embedding-3-small'
)

client = chromadb.Client()

try:
    client.delete_collection(name='server_logs')
except:
    pass

collection = client.get_or_create_collection(name='server_logs.txt', embedding_function=openai_eb)

def ingestao_logs_do_arquivo():
    if not os.path.exists(LOG_FILE):
        print(f'Arquivo {LOG_FILE} não encontrado.')
        print('Por favor crie este arquivo na mesma pasta e ensira o arquivo de logs')
        return 
    print(f'lendo logs do arquivo {LOG_FILE}')

    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        logs = [line.strip() for line in f.readlines() if line.strip()]
    
    if not logs:
        print(f'Nenhum log encontrado no arquivo {LOG_FILE}')
        return
    print(f'gerando encondings para {len(logs)} logs')

    ids=[f'log_{i}' for i in range(len(logs))]

    metadatas=[{'source': LOG_FILE, 'timestamp': datetime.datetime.now().isoformat(),} for _ in logs]

    collection.add(
        documents=logs,
        metadatas=metadatas,
        ids=ids
    )   

    print(f'encondings gerados com sucesso para {len(logs)} logs')

ingestao_logs_do_arquivo()
@mcp.tool()
def search_logs(query: str, n_results: int = 3) -> str:
    print(f'pesquisando por {query}')
    if collection.count() == 0:
        return 'Nenhum log encontrado'
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    found_logs=results['documents'][0]
    distances = results['distances'][0]
    
    response = f'Resultados de investigação para {query} \n'

    for log, dist in zip(found_logs, distances):
        relevance = round((1 - dist) * 100, 2)
        response += f'[Relevancia: {relevance}% LOG: {log}]\n'
    
    return response

@mcp.tool()
def get_log_statistics() -> str:
    count = collection.count()
    return f'o sistema LogSense possui atualmente {count} logs carregados do arquivo {LOG_FILE}'

@mcp.tool()
def block_ip_firewall(ip_adress: str, reason: str) -> str:
    action_log = f'[AÇÃO DEFENSIVA] o ip {ip_adress} foi bloqueado.'
    details = f'motivo: {reason}'

    print('\n' + '='*40)
    print(action_log)
    print(details)
    print('='*40 + '\n')
    
    return f'O ip {ip_adress} foi bloqueado com sucesso por motivo: {reason}'

if __name__== '__main__':
    print('servidor mcp rodando')
    mcp.run()