import asyncio.base_futures
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def conectar_db():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def tool_inspect_permission():
    conn = conectar_db()
    cursor = conn.cursor()
    query = """
    SELECT grantee, table_name, privilege_type
    FROM information_schema.role_table_grants
    WHERE grantee = 'PUBLIC' AND table_schema = 'public'
    """
    
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    
    if not result:
        return 'Nenhuma permissão de risco (PUBLIC) encontrada.'

    report = "Permissões Publicas encontradas \n -ALERTA DE SEGURANÇA!\n"
    
    for row in result:
        report += f'Usuario: {row[0]} | tabela: {row[1]} | permissão: {row[2]}\n'

    return report

def tool_execute_contaiment(sql_command):
    conn = conectar_db()
    cursor = conn.cursor()

    try:
        cursor.execute(sql_command)
        conn.commit()
        msg = f'Comando SQL executado com sucesso: {sql_command}'

    except Exception as e:
        conn.rollback()
        msg = f'Erro ao executar comando SQL: {str(e)}'

    finally:
        conn.close()
    
    return msg