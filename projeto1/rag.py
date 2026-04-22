# Importações
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

#modelo de embedding de IA - HuggingFace
EMBEDDING_MODEL = "sentece-transformers/all-MiniLM-L6-v2"

#funções
def get_retriver(path_pdf: str):
    print(f'Carregando pdf: {path_pdf}')

    loader = PyPDFLoader(path_pdf)

    documents = loader.load()

    if not documents:
        print("nenhum documento foi inserido")
        return None
    
    split_text = RecursiveCharacterTextSplitter(chunk_size = 100, chunk_overlap = 150)

    chunk = split_text.split_documents(documents)

    if not chunk:

        print('nao foi possivel dividir o documento em chunks')
        return None
    
    print(f"o documento foi dividio em {len(chunk)} chunks")

    #Embedding
    embeddings = HuggingFaceEmbeddings(model_name = EMBEDDING_MODEL, cache_folder = os.path.join(os.getcwd(), ".cache"))

    try:

        vectordb = FAISS.from_documents(chunk, embeddings)
        print("VectorDB criado com sucesso")

    except Exception as e:

        print(f"Não foi possivel criar o VectorDb por: {e}")
        return None
    
    return vectordb.as_retriever(search_kwargs = {"k" : 3})

