# Desafio: Ingestão e Busca Semântica com LangChain e Postgres

## Objetivo
Você deve entregar um software capaz de:
- **Ingestão**: Ler um arquivo PDF e salvar suas informações em um banco de dados PostgreSQL com extensão pgVector.
- **Busca**: Permitir que o usuário faça perguntas via linha de comando (CLI) e receba respostas baseadas apenas no conteúdo do PDF.

## Exemplo no CLI
Faça sua pergunta:
> PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
> RESPOSTA: O faturamento foi de 10 milhões de reais.

---

Perguntas fora do contexto:
> PERGUNTA: Quantos clientes temos em 2024?
> RESPOSTA: Não tenho informações necessárias para responder sua pergunta.

## Tecnologias Obrigatórias
- Linguagem: Python
- Framework: LangChain
- Banco de dados: PostgreSQL + pgVector
- Execução do banco de dados: Docker & Docker Compose

## Pacotes Recomendados
- **Split**: `from langchain_text_splitters import RecursiveCharacterTextSplitter`
- **Embeddings (OpenAI)**: `from langchain_openai import OpenAIEmbeddings`
- **Embeddings (Gemini)**: `from langchain_google_genai import GoogleGenerativeAIEmbeddings`
- **PDF**: `from langchain_community.document_loaders import PyPDFLoader`
- **Ingestão**: `from langchain_postgres import PGVector`
- **Busca**: `similarity_search_with_score(query, k=10)`

## Modelos
### OpenAI
- Modelo de embeddings: `text-embedding-3-small`
- Modelo de LLM para responder: `gpt-4o-mini` (Assumindo gpt-4o-mini, pois gpt-5-nano não existe)

### Gemini
- Modelo de embeddings: `models/embedding-001`
- Modelo de LLM para responder: `gemini-2.5-flash-lite`

## Requisitos
### 1. Ingestão do PDF
- O PDF deve ser dividido em chunks de 1000 caracteres com overlap de 150.
- Cada chunk deve ser convertido em embedding.
- Os vetores devem ser armazenados no banco de dados PostgreSQL com pgVector.

### 2. Consulta via CLI
Criar um script Python para simular um chat no terminal. Passos:
1. Vetorizar a pergunta.
2. Buscar os 10 resultados mais relevantes (k=10) no banco vetorial.
3. Montar o prompt e chamar a LLM.
4. Retornar a resposta ao usuário.

**Prompt a ser utilizado**:
```text
CONTEXTO:
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
```

## Estrutura Obrigatória do Projeto
```
├── docker-compose.yml
├── requirements.txt      # Dependências
├── .env.example          # Template da variável OPENAI_API_KEY
├── src/
│   ├── ingest.py         # Script de ingestão do PDF
│   ├── search.py         # Script de busca
│   ├── chat.py           # CLI para interação com usuário
├── document.pdf          # PDF para ingestão
└── README.md             # Instruções de execução
```

---

# Plano de Execução

Abaixo está o descritivo de tarefas e etapas para concluir com sucesso este desafio:

## Fase 1: Preparação do Ambiente
1. **Verificação dos Arquivos**: Checar a existência de todos os arquivos no template providenciado (especialmente `docker-compose.yml`, `requirements.txt` e o arquivo `document.pdf`).
2. **Criação do Ambiente Virtual**:
   - `python3 -m venv venv`
   - Ativação: `source venv/bin/activate` (Linux/Mac) ou `.\venv\Scripts\Activate.ps1` (Windows PowerShell).
3. **Instalação de Dependências**:
   - Rodar `pip install -r requirements.txt`.
4. **Configuração de Chaves (API Keys)**:
   - Duplicar o aquivo `.env.example` para `.env` e preencher com a `OPENAI_API_KEY` ou `GOOGLE_API_KEY` de acordo com a escolha (OpenAI ou Gemini).

## Fase 2: Infraestrutura (Banco de Dados)
1. **Subir o Banco de Dados**:
   - Executar no terminal: `docker compose up -d`
2. **Verificar a Execução**:
   - Garantir que o container está saudável e que a instância PostgreSQL está rodando com a extensão de Vetor (pgVector) instalada e operante na porta designada.
   - Variáveis comuns de conexão: `postgresql+psycopg://postgres:postgres@localhost:5432/postgres` (verificar credenciais no seu docker-compose.yml).

## Fase 3: Desenvolvimento - Ingestão (`src/ingest.py`)
1. **Carregar Documento**:
   - Inicializar `PyPDFLoader` com o arquivo `../document.pdf` (ou caminho relativo correto).
2. **Corte em Chunks**:
   - Inicializar `RecursiveCharacterTextSplitter` configurado para `chunk_size=1000` e `chunk_overlap=150`.
   - Gerar os sub-documentos usando `split_documents`.
3. **Setup de Banco Vetorial e Embeddings**:
   - Configurar o provedor de Embedding (e.g. `OpenAIEmbeddings(model="text-embedding-3-small")`).
   - Inicializar a classe `PGVector` de `langchain_postgres`.
4. **Armazenamento**:
   - Adicionar ou indexar os documentos processados gerando os embeddings e salvando via operação vector store.

## Fase 4: Desenvolvimento - Busca e Interface CLI (`src/chat.py` e `src/search.py`)
1. **Lógica de Busca Vetorial (`src/search.py` - dependendo da arquitetura e utilitário desejados)**:
   - Fazer uma função isolada que constrói a conexão do `PGVector`.
   - Função utilitária usando a instância do vector store para chamar `similarity_search_with_score(query, k=10)`.
2. **Construção do Prompt Core (`src/chat.py`)**:
   - Definir a template com as restrições indicadas (REGRAS e EXEMPLOS de FORA DO CONTEXTO).
3. **LLM Chain e Execução do Chat (`src/chat.py`)**:
   - Instanciar a LLM (ex: `ChatOpenAI(model="gpt-4o-mini", temperature=0)` ou `ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")`).
   - Entrar em um laço de repetição (`while True:`) lendo input do usuário usando `input("Faça sua pergunta: ")`.
   - Adicionar comando de escape (ex: se digitar "sair" ou "exit", encerra o laço).
   - Fazer a vetorização e busca dos resultados no banco para a query recebida.
   - Formatar os documentos recuperados como string (concatenate o conteúdo textual de cada um).
   - Subsidiar o prompt com os documentos injetados na variável `{resultados concatenados do banco de dados}`.
   - Chamar e apresentar a resposta da LLM formatada ao usuário.

## Fase 5: Testes e Validação
1. **Ingestão**:
   - Rodar `python src/ingest.py`. Verificar se concluiu sem erro e se tabelas de embeddings foram preenchidas no PG (pode usar um dbeaver/pgadmin opcionalmente).
2. **Consulta e Resposta**:
   - Iniciar o sistema executando `python src/chat.py`.
   - Testar o caminho feliz: "Qual o faturamento da Empresa SuperTechIABrazil?". A resposta deve ser compatível com os dados do arquivo PDF, e nenhuma invenção deve ocorrer.
   - Testar os caminhos fora de escopo: "Qual é a capital da França?" ou "Quantos clientes temos em 2024?". O sistema DEVE retornar obrigatoriamente: *"Não tenho informações necessárias para responder sua pergunta."*

## Fase 6: Finalização do Desafio
1. **Atualização do README**:
   - Preencher o `README.md` com explicações do seu passo-a-passo para instalar requisitos, dar start no docker, e executar os scripts.
2. **Push Final**:
   - Realizar os devidos `git add`, `git commit` e `git push` no repositório final/fork para entregar.
