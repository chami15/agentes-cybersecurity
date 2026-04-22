import socket
import mysql.connector
from langchain_core.tools import tool

def sql_safety_guardrail(query: str) -> bool:
    """Impede execução de comandos destrutivos."""
    forbbiden_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'GRANT', 'FLUSH']

    if any(keyword in query.upper() for keyword in forbbiden_keywords):
        return False
    return True

@tool
def port_scan_tool(ip: str, port: int) -> str:
    """Verifica se a porta do banco de dados está aberta."""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.settimeout(2)

    result = sock.connect_ex((ip, port))

    sock.close()   

    if result == 0: 
        return "OPEN"
    return "CLOSED"

@tool
def mysql_login_check(ip:str,user:str,password_list:list) -> str:
    """Tenta força bruta controlada para validar credenciais fracas."""
    for pwd in password_list:
        try:

            conn = mysql.connector.connect(host=ip,user = user, password = pwd, connect_timeout = 3)
            if conn.is_connected():
                conn.close()
                return f'Sucesso: senha encontrada para o usuario: {user} : {pwd}'
            
        except mysql.connector.Error:
            continue

    return f'Falha: Nenhuma senha fraca foi encontrada'

@tool
def safe_sql_query(ip:str, user:str, pwd: str, query: str) -> str:
    """Executa queries SQL de leitura com Guardrails aplicados."""
    if not sql_safety_guardrail(query):
        return 'Guardrail Alerta: comando destrutivo foi bloqueado'
    
    try: 
        conn = mysql.connector.connect(host=ip, user = user, password = pwd)

        cursor = conn.cursor()
        cursor.execute(query)

        results = cursor.fetchall()
        conn.close()

        return str(results)
    
    except Exception as e:
        return f'Erro: {e}'


