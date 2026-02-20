import os
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from search import get_vector_store

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH", "document.pdf")

def is_ingested():
    try:
        vector_store = get_vector_store()
        results = vector_store.similarity_search("teste", k=1)
        return len(results) > 0
    except Exception:
        return False

def ingest_pdf():
    if not os.path.exists(PDF_PATH):
        print(f"Erro: Arquivo '{PDF_PATH}' não encontrado.")
        return

    print(f"Carregando documento de: {PDF_PATH}")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    print("Dividindo o texto em chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    chunks = text_splitter.split_documents(documents)

    print("Conectando ao banco de dados e armazenando embeddings...")
    try:
        vector_store = get_vector_store()
        batch_size = 10
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            vector_store.add_documents(batch)
            print(f"Injetando Documentos:: Lote {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}", flush=True)
            time.sleep(2) # Tratativa para evitar Rate Limit (429) em Tiers gratuitos

        print("Ingestão concluída com sucesso!")
    except Exception as e:
        print(f"Erro durante a ingestão: {e}")

if __name__ == "__main__":
    ingest_pdf()