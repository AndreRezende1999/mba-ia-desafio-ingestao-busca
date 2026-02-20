import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from search import search_prompt

load_dotenv()

def get_llm():
    """Returns the correct LLM based on available API Keys."""
    if os.getenv("OPENAI_API_KEY"):
        # The prompt requested 'gpt-4o-mini', using it as fallback if not overridden
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    elif os.getenv("GOOGLE_API_KEY"):
        model_name = os.getenv("GOOGLE_CHAT_MODEL", "gemini-2.5-flash-lite")
        return ChatGoogleGenerativeAI(model=model_name, temperature=0, max_tokens=1000)
    else:
        raise ValueError("Nenhuma API Key configurada para instanciar o LLM.")
from search import search_prompt
from ingest import ingest_pdf, is_ingested

def main():
    try:
        if not is_ingested():
            print("Executando a ingestão de documentos pela primeira vez...")
            ingest_pdf()
        else:
            print("Documentos já ingeridos. Pulando a etapa de ingestão...")
    except Exception as e:
        print(f"Erro na verificação de ingestão: {e}")
    
    try:
        llm = get_llm()
    except Exception as e:
        print(f"Erro ao carregar LLM: {e}")
        return

    while True:
        try:
            query = input("Faça sua pergunta: ")
        except (KeyboardInterrupt, EOFError):
            break
            
        if query.strip().lower() in ['sair', 'exit', 'quit']:
            break
            
        if not query.strip():
            continue
            
        try:
            prompt_text = search_prompt(question=query)
            if not prompt_text:
                print("Nenhum contexto encontrado no banco de dados. Realize a ingestão primeiro.")
                continue
            response = llm.invoke(prompt_text)
            print(f"RESPOSTA: {response.content}")
        except Exception as e:
            print(f"Erro durante a execução do chat: {e}")

if __name__ == "__main__":
    main()