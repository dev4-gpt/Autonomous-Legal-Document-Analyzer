### 🚀 Autonomous Legal Document Analyzer
#### Week 1 AI Project – Cursor Setup Notes & Rules (Updated)

---

## 🚀 Project Overview
This project is an autonomous AI system that:
- Ingests legal contracts automatically from a folder
- Extracts and summarizes key legal clauses
- Classifies document type (e.g., NDA, SLA, MSA)
- Assesses clause-level legal risk
- Presents results in a Streamlit UI
- Runs fully locally (Ollama), or with OpenAI/Anthropic APIs
- Deployable in a Docker container

---

## 🧱 Tech Stack

| Component              | Tools                                                  |
|------------------------|--------------------------------------------------------|
| **LLM**               | Ollama (Llama 3, Mistral, etc. — local, default), OpenAI, or Anthropic (Claude) |
| **RAG Engine**        | LangChain                                              |
| **Vector DB**         | FAISS (local) or ChromaDB (scalable)              |
| **UI**                | Streamlit                                              |
| **Agent Framework**   | LangChain Agents or LangGraph                          |
| **Watcher**           | `watchdog` for real-time folder monitoring             |
| **Parsers**           | `unstructured`, `PyMuPDF`, `python-docx`, `BeautifulSoup` (for HTML) |
| **Monitoring (Optional)** | LangSmith for prompt tracing and debugging       |
| **Deployment**        | Docker + `.dockerignore`                              |
| **Persistence (Optional)** | SQLite for clause/risk log history              |

---

## 🦙 Local LLM (Ollama) Setup

### Requirements
- Mac (Apple Silicon or recent Intel recommended)
- At least 8GB RAM (16GB+ recommended)
- 5GB+ free disk space

### Steps
1. **Install Ollama:**  
   Download and install from [https://ollama.com/download](https://ollama.com/download)
2. **Pull the Llama 3 model:**  
   ```bash
   ollama pull llama3
   ```
3. **Start the model:**  
   ```bash
   ollama run llama3
   ```
   Leave this running in the background.
4. **Set your `.env` file:**  
   ```
   LLM_PROVIDER=ollama
   ```
5. **Run the watcher:**  
   ```bash
   python src/watcher.py
   ```
6. **Run the Streamlit UI:**  
   ```bash
   streamlit run src/ui.py
   ```

### Switching LLM Providers
- To use OpenAI or Anthropic, set `LLM_PROVIDER=openai` or `LLM_PROVIDER=anthropic` in your `.env` and provide the appropriate API key.

---

## 📁 Directory Structure
```
autonomous_legal_analyzer/
├── data/uploads/            # Incoming contracts (PDF/DOCX/TXT/HTML)
├── data/analysis/           # Analyzed contract results (JSON)
├── data/vectorstore/        # Vector DB for contract chunks
├── src/
│   ├── watcher.py           # Watches folder and triggers analysis
│   ├── parser.py            # Extracts + cleans text from contracts
│   ├── embedder.py          # Embeds chunks + stores in FAISS/Chroma
│   ├── agent.py             # Multi-step agent: classify, extract, risk, summarize
│   ├── ui.py                # Streamlit frontend
│   └── config.py            # Env vars, constants, and keys
├── app.py                   # Main runtime script
├── .env                     # Model keys and config
├── .dockerignore            # Ignore heavy/unneeded files in build
├── Dockerfile               # Container setup
├── requirements.txt         # Project dependencies
└── README.md                # You are here
```

---

## 🧠 Agent Capabilities

1. **Contract Classification** (NDA, SLA, MSA, etc.)
2. **Clause Extraction** (Termination, Indemnity, Confidentiality, etc.)
3. **Risk Scoring** (Low / Medium / High + rationale)
4. **Document Summarization**

**Example Output:**
```json
{
  "contract_type": "NDA",
  "clauses": [ ... ],
  "risks": [ ... ],
  "summary": "This NDA outlines confidentiality terms..."
}
```

---

## 📝 Prompt Strategy

Use few-shot examples for consistency:

- Clause Extraction:
  > "Extract the *Indemnity* clause from this contract."
- Risk Scoring:
  > "Rate the *Termination* clause as Low, Medium, or High risk with 1-sentence justification."
- Contract Classification:
  > "Classify this document: NDA, SLA, MSA, or Other?"

Use `LangChain.PromptTemplate` with dynamic placeholders.

---

## 🔁 Workflow Overview

1. `watcher.py` detects new file in `data/uploads/`
2. `parser.py` cleans and extracts text
3. `embedder.py` splits + embeds chunks into FAISS/Chroma
4. `agent.py` runs:
   - Classification
   - Clause Extraction
   - Risk Scoring
   - Summarization
5. `ui.py` displays results in Streamlit

---

## 🛠️ Setup Checklist

- [ ] Create `data/uploads/` and `logs/` folders
- [ ] Install dependencies with `pip install -r requirements.txt`
- [ ] Implement core files: `watcher.py`, `parser.py`, `agent.py`, etc.
- [ ] Add `.env` with keys: `OPENAI_API_KEY`, etc.
- [ ] Write Streamlit UI
- [ ] Add `.dockerignore`
- [ ] Build and test Docker container

---

## 🧩 Dev Tips

- Use `RecursiveCharacterTextSplitter` (LangChain) for clean chunking
- Run local model via:
  ```bash
  ollama run llama3
  ```
- Set up LangSmith for trace-based debugging (optional)
- Add `pytest` tests for `parser.py`, `agent.py`
- Use color-coded UI (red/yellow/green) for risk visualization

---

## 📦 Analyzed File Storage
- All analyzed contract results are stored as JSON in `data/analysis/`.
- The Streamlit UI reads from this folder to display results.

## ✅ Project Capabilities
- Upload any contract to `data/uploads/` (PDF, DOCX, TXT, HTML)
- Fully local pipeline (no API/credit issues with Ollama)
- Switchable LLMs (Ollama, OpenAI, Anthropic)
- Clause extraction, risk scoring, contract classification, summarization
- Modern, color-coded UI for risk visualization

## 🛠️ Dev Tips
- Use `LLM_PROVIDER` in `.env` to switch LLMs
- Use `ollama run llama3` to start the local LLM
- Add more clause types or risk logic in `src/agent.py`
- Add more file types in `src/parser.py`

---

**This project is a fully autonomous, local-first legal document analyzer.**
- No API limits, no cloud costs, and easy to run on any capable Mac.
- For cloud or API-based use, just set the provider and key in `.env`.

---

## Project Structure
```
autonomous_legal_analyzer/
├── data/
│   └── uploads/           # Contracts + labels (populated by scripts)
├── scripts/
│   ├── load_cuad.py       # CUAD loader
│   ├── crawl_edgar.py     # EDGAR crawler
│   └── curate_prompts.py  # Prompt template generator
├── prompts/
│   └── prompt_examples.json  # Prompt templates
├── src/
│   └── ...                # Main app code
├── requirements.txt
├── README.md
└── .env.example
```

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd autonomous_legal_analyzer
```

### 2. Create a Virtual Environment & Install Requirements
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
> **Note:** All required packages, including `beautifulsoup4` (for `bs4`), are listed in `requirements.txt`.

### 3. Populate `/data/uploads/` with Contracts

#### a. Download CUAD Contracts
Run the CUAD loader script to download and extract contracts:
```bash
python scripts/load_cuad.py
```
This will populate `data/uploads/` with sample contracts and labeled clause metadata.

#### b. (Optional) Download Real Contracts from EDGAR
Run the EDGAR crawler to fetch additional contracts:
```bash
python scripts/crawl_edgar.py
```

### 4. Generate Prompt Templates
```bash
python scripts/curate_prompts.py
```
This will create `prompts/prompt_examples.json` with ready-to-use prompt templates.

### 5. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your API keys and model config as needed.

### 6. Run the Main Application
```bash
streamlit run src/ui.py
```

---

## Data Sources
- **CUAD**: [Contract Understanding Atticus Dataset](https://github.com/TheAtticusProject/cuad)
- **EDGAR**: [SEC EDGAR Filings](https://www.sec.gov/edgar/search/)
- **Law Insider**: [Free Contracts](https://www.lawinsider.com/contracts)

---

## Scripts
- `scripts/load_cuad.py`: Downloads and processes CUAD contracts
- `scripts/crawl_edgar.py`: Fetches real contracts from EDGAR
- `scripts/curate_prompts.py`: Generates prompt templates for clause extraction, risk scoring, and classification

---

## Troubleshooting

### ImportError: No module named 'bs4'
If you see an error like:
```
Import "bs4" could not be resolved from source
```
Run:
```bash
pip install beautifulsoup4
```
Make sure your virtual environment is activated.

---

## Learn More
- See `src/` for the main app code and workflow
- See `prompts/` for prompt engineering examples
- See `data/uploads/` for contract samples (after running scripts)

---

## License
MIT 



