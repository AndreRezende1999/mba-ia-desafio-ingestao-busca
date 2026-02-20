# Desafio MBA Engenharia de Software com IA - Full Cycle

### Ordem de execução

1. Subir o banco de dados:
```bash
docker compose up -d
```

2. Crie e ative um ambiente virtual:
```bash
# Linux/MacOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as chaves de API:
Copie o arquivo `.env.example` para `.env` e preencha a chave escolhida (OpenAI ou Gemini).

5. Executar ingestão do PDF:
```bash
python src/ingest.py
```

6. Rodar o chat:
```bash
python src/chat.py
```