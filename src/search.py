import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres.vectorstores import PGVector

load_dotenv()

def get_embeddings_model():
    """Returns the correct embedding model based on available API Keys."""
    if os.getenv("OPENAI_API_KEY"):
        model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        return OpenAIEmbeddings(model=model_name)
    elif os.getenv("GOOGLE_API_KEY"):
        model_name = os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001")
        return GoogleGenerativeAIEmbeddings(model=model_name)
    else:
        raise ValueError("Nenhuma API Key configurada. Por favor, adicione OPENAI_API_KEY ou GOOGLE_API_KEY no arquivo .env")

def get_vector_store():
    """Initializes and returns the PGVector store."""
    connection_string = os.getenv("DATABASE_URL")
    collection_name = os.getenv("PG_VECTOR_COLLECTION_NAME", "challenge_docs")
    
    if not connection_string:
        raise ValueError("DATABASE_URL não configurada no .env")

    embeddings = get_embeddings_model()
    
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection_string,
        use_jsonb=True,
    )
    
    return vector_store

PROMPT_TEMPLATE = """CONTEXTO:
{resultados concatenados do banco de dados}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta do usuário}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def search_prompt(question=None):
    """
    Busca os documentos relevantes e retorna o prompt formatado
    junto com os chunks encontrados.
    """
    if not question:
        return ""
        
    vector_store = get_vector_store()
    # Utilizando k=10 como exigido nas instruções do desafio (fase 4 do plano)
    results = vector_store.similarity_search_with_score(question, k=10)
    
    if not results:
        return ""
        
    concatenated_context = "\n\n".join([doc.page_content for doc, score in results])
    
    prompt = PROMPT_TEMPLATE.format(
        **{
            "resultados concatenados do banco de dados": concatenated_context,
            "pergunta do usuário": question
        }
    )
    return prompt