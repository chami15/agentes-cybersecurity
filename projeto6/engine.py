import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import zmq
import zmq.asyncio
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class TriagemResult(BaseModel):
    is_threat: bool = Field(description='True se for ameaça, False se for seguro')
    severity: str = Field(description="use APENAS: LOW, MEDIUM, HIGH, CRITICAL")
    category: str = Field(description="Ex: SQL Injection, Leaked Key, Misconfig")
    reasoning: str = Field(description="Explicção curta")

class RemediationResults(BaseModel):
    action_plan: str = Field(description="Explicação do que deve fazer")
    code_fix: str = Field(description="Comando ou codigo exato para corrigir")

class AISecurityEngine:
    def __init__(self):
        self.llm = OllamaLLM(model='llama3', temperature=0.2)
        self.ctx = zmq.asyncio.Context()
        self.sub_socket = self.ctx.socket(zmq.SUB)
        self.sub_socket.connect('tcp://localhost:5555')
        self.sub_socket.subscribe("")
        self.pub_socket = self.ctx.socket(zmq.PUB)
        self.pub_socket.bind('tcp://*:5556')
    
    async def ai_agent_run_triage(self, log_data):
        print(f'Analisando {log_data['source']}...')

        parser = JsonOutputParser(pydantic_object=TriagemResult)

        prompt = PromptTemplate(
            template = """
            Você é um Analista de Segurança Sênior. Classifique o log.
            
            REGRAS DE SEVERIDADE OBRIGATÓRIAS:
            - "Acesso público via ACL" -> HIGH
            - "Detectado payload" ou "SQL" -> CRITICAL
            - "Access Key ID encontrada" -> CRITICAL
            - "Privileged=true" -> MEDIUM
            - Login normal -> LOW (is_threat: false)

            Log: {log}
            Origem: {src}
            
            Responda ESTRITAMENTE o JSON:
            {fmt}
            """,
            
            input_variables = ["log", "src"],
            
            partial_variables = {"fmt": parser.get_format_instructions()},
        )

        chain = prompt | self.llm | parser

        try: 
            res = await chain.ainvoke({'log': log_data['raw_log'], 'src': log_data['source']})
            return TriagemResult(**res)
        except Exception as e:
            print(f'Erro de triagem: {e}')

            return None
        
    async def ai_agent_run_remediation(self, log_data, triage):
        print(f"Engenheiro em ação: Criando fix para {triage.category}...")

        parser = JsonOutputParser(pydantic_object=RemediationResults)

        prompt = PromptTemplate(
            template = """
            Aja como um Engenheiro DevSecOps Senior.
            Gere uma correção técnica para esta vulnerabilidade.
            
            Vulnerabilidade: {cat}
            Log Original: {log}
            
            Se for AWS S3 -> Forneça comando CLI 'aws s3api put-bucket-acl...' para remover public access.
            Se for SQL Injection -> Mostre código Python parametrizado ou regra de WAF.
            Se for Payload Detected -> Mostre código Python parametrizado ou regra de WAF.
            Se for Leaked Key -> Mostre comando para revogar a chave (aws iam delete-access-key).
            Se for K8s Privileged -> Mostre o YAML corrigido (securityContext: privileged: false).

            Responda ESTRITAMENTE o JSON:
            {fmt}
            """,
            
            # Define as variáveis de entrada do prompt
            input_variables = ["cat", "log"],
            
            # Injeta o formato esperado do parser
            partial_variables = {"fmt": parser.get_format_instructions()},
        )

        chain = prompt | self.llm | parser

        try: 
            res = await chain.ainvoke({'cat': triage.category, 'log': log_data['raw_log']})
            return RemediationResults(**res)
        except Exception as e:
            print(f"Erro na remediação: {e}")
            return None
        
    async def start(self):
        print("O sistema esta ativado, aguardando eventos..")

        while True:
            event = await self.sub_socket.recv_json()

            triage = await self.ai_agent_run_triage(event)

            if triage and triage.is_threat:
                trigger_fix = False

                if triage.severity in ['MEDIUM', "HIGH", "CRITICAL"]:
                    trigger_fix = True

                if 'S3' in triage.category or 'Key' in triage.category:
                    trigger_fix = True

                remediation = None

                if trigger_fix:
                    remediation = await self.ai_agent_run_remediation(event, triage)

                alert_packet = {
                    "type": "ALERT",
                    "original_event": event,
                    "triage": triage.model_dump(), 
                    "remediation": remediation.model_dump() if remediation else None
                }

                await self.pub_socket.send_json(alert_packet)

                print(f'Alerta publicado: {triage.category} | Fix gerado: {remediation is not None}')

if __name__ == "__main__":
    engine = AISecurityEngine()
    try: 
        asyncio.run(engine.start())
    except KeyboardInterrupt:
        print("O engine foi parado")

