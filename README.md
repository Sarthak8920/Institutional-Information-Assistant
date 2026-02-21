# CampusConnect_AI — GL Bajaj RAG

A production-ready **Retrieval-Augmented Generation (RAG)** application that answers questions about **GL Bajaj Institute of Technology and Management (GLBITM)** using scraped campus content, local embeddings, and Groq's LLaMA 3.1.

---

## Overview

CampusConnect_AI lets users ask natural-language questions about placements, leadership, admissions, departments, and other institutional information. It combines:

- **Web scraping** of [glbitm.org](https://www.glbitm.org) for relevant pages  
- **Local embeddings** (HuggingFace `all-MiniLM-L6-v2`) — no embedding API key required  
- **FAISS** for fast similarity search over chunked documents  
- **Groq** (LLaMA 3.1 8B Instant) for low-latency, context-grounded answers  
- **Streamlit** for a simple chat UI, plus a **CLI** for scripting

Answers are grounded in the retrieved context; if the answer is not in the context, the model responds with *"Information not available on the website."*

---

## Features

- **RAG pipeline**: Scrape → clean & deduplicate → chunk → embed → index (FAISS) → query with LLM  
- **Keyword-focused scraping**: Targets pages about leadership, placements, admissions, departments, TPO, etc.  
- **Chat interface**: Streamlit app with session history and spinner feedback  
- **CLI mode**: `query.py` for interactive or scripted Q&A  
- **No embedding API**: Uses sentence-transformers locally; only Groq API key needed for the LLM  

---

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌─────────────┐
│  scrape.py  │ ──► │ clean_text.txt   │ ──► │ build_vectorstore│ ──► │ faiss_index/│
│  (glbitm)   │     │ (cleaned text)   │     │ (chunk+embed)    │     │ (FAISS+pkl) │
└─────────────┘     └──────────────────┘     └─────────────────┘     └──────┬──────┘
                                                                              │
                                                                              ▼
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐     ┌─────────────┐
│   app.py    │ ◄── │ RAG chain        │ ◄── │ Retriever (k=2)  │ ◄── │ Embeddings  │
│ (Streamlit) │     │ (Groq LLaMA 3.1) │     │                 │     │ (MiniLM)    │
└─────────────┘     └──────────────────┘     └─────────────────┘     └─────────────┘
       │
       │  (alternative)
       ▼
┌─────────────┐
│  query.py   │  (CLI)
└─────────────┘
```

---

## Prerequisites

- **Python 3.10+** (tested with 3.12)  
- **Groq API key** — [Create one](https://console.groq.com/)  
- Enough RAM for sentence-transformers (~500MB+) and FAISS index  

---

## Setup

### 1. Clone and enter the project

```bash
cd glb_Rag
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment variables

Create a `.env` file in the project root (see [.gitignore](#security) — never commit this):

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## Usage

### One-time: Build the knowledge base

1. **Scrape** the website (writes `clean_text.txt`):

   ```bash
   python scrape.py
   ```

2. **Build the FAISS index** from `clean_text.txt` (creates/overwrites `faiss_index/`):

   ```bash
   python build_vectorstore.py
   ```

### Run the app or CLI

- **Streamlit chat UI** (default port 8501):

  ```bash
  streamlit run app.py
  ```

- **CLI** (interactive loop; type `exit` to quit):

  ```bash
  python query.py
  ```

---

## Project structure

```
glb_Rag/
├── README.md              # This file
├── .env                   # GROQ_API_KEY (do not commit)
├── .gitignore
├── requirements.txt       # Python dependencies
├── scrape.py              # Scrape glbitm.org → clean_text.txt
├── clean_text.txt         # Scraped/cleaned corpus (generated)
├── build_vectorstore.py   # Chunk + embed + save FAISS index
├── faiss_index/           # FAISS index + pkl (generated)
│   ├── index.faiss
│   └── index.pkl
├── query.py               # CLI Q&A using RAG chain
└── app.py                 # Streamlit chat app
```

---

## Tech stack

| Component        | Technology                          |
|-----------------|-------------------------------------|
| LLM             | Groq — LLaMA 3.1 8B Instant         |
| Embeddings      | HuggingFace — all-MiniLM-L6-v2      |
| Vector store    | FAISS (CPU)                         |
| Orchestration   | LangChain (LCEL, prompts, retriever) |
| Scraping        | Beautiful Soup, requests             |
| UI              | Streamlit                           |
| Config          | python-dotenv (.env)                 |

---

## Configuration notes

- **Retriever**: `app.py` uses `k=2` chunks; `query.py` uses `k=5`. Adjust in each file if needed.  
- **Chunking**: `build_vectorstore.py` uses `chunk_size=1000`, `chunk_overlap=200`. Change there to re-index.  
- **Model**: Both app and CLI use `llama-3.1-8b-instant` and `temperature=0`.  

---

## Rebuilding the index

After updating `clean_text.txt` (e.g. re-running `scrape.py` or editing manually):

```bash
python build_vectorstore.py
```

Then restart the Streamlit app or CLI.

---

## Security

- **Do not commit** `.env` or any file containing `GROQ_API_KEY`.  
- `.gitignore` is set up to exclude `.env`, `venv/`, and generated data if desired.  

---

## License

Use and modify as needed for GL Bajaj / GLBITM internal or approved use.
