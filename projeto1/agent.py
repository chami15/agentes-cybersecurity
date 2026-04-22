# Importações
import os
from typing import Annotated, List
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# funções
def cria_rag_tool(retriver):

    @tool
    def check_security_policy(query:str):
        print(f'Ferramenta RAG esta consultando: {query}')

        if query is None:
            return "erro: a ferramenta não conseguiu acessar nenhum documento"
        
        try:
            docs = retriver.invoke(query)
            context = '\n\n----\n\n'.join([doc.page_content for doc in docs])
            if not context:
                return "Nenhuma informação relevante foi encontrada"
            return f"Informação da politica relevante encontrada: {context}"
        
        except Exception as e:
            return f"Erro por causa de: {e}"

    return check_security_policy    
    
class AgentState(TypedDict):
    messages : Annotated[list, add_messages]

class CyberSecurityAgent:

    def __init__(self, retriver):

        if not os.getenv("GROQ_API_KEY"):
            raise EnvironmentError("GROQ_API_KEY não encontrado no .env")
        
        self.llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

        rag_tool = cria_rag_tool(retriver)

        self.tools = [rag_tool]

        self.model_with_tool = self.llm.bind_tools(self.tools)

        self.graph = self.build_graph()

    def build_graph(self):
        graph_builder = StateGraph(AgentState)
        graph_builder.add_node("agent", self.call_model)

        tool_node = ToolNode(self.tools)

        graph_builder.add_node("tools", tool_node)
        graph_builder.set_entry_point('agent')

        graph_builder.add_conditional_edges(
            "agent",
            self.should_continue,
            {
            "tools" : 'tools',
            END : END
            }
        )
        graph_builder.add_edge('agent', 'tools')

        return graph_builder.compile()
    
    def should_continue(self, state: AgentState):
        
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tools"
        
        return END
    
    def call_model(self, state:AgentState):
        print("----Nó do Agente----")
        
        messages = state["messages"]
        response = self.model_with_tool.invoke(messages)

        return {"messages" : [response]}
    
def criar_agente(retriver):
    agent_instance = CyberSecurityAgent(retriver)
    return agent_instance.graph
    




    
    