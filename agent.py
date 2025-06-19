"""
Agent module for contract analysis.
Supports LLMs: Ollama (local, default), OpenAI, Anthropic.
Switch LLM by setting the LLM_PROVIDER environment variable to 'ollama', 'openai', or 'anthropic'.
"""
import os
from dotenv import load_dotenv
load_dotenv()
from langchain.prompts import PromptTemplate
import re

# LLM imports
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

if LLM_PROVIDER == "openai":
    from langchain_openai import OpenAI
    LLM = OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
elif LLM_PROVIDER == "anthropic":
    from langchain_anthropic import ChatAnthropic
    LLM = ChatAnthropic(model="claude-3-opus-20240229", anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"))
else:  # Default to Ollama
    from langchain_ollama import OllamaLLM
    LLM = OllamaLLM(model="llama3")  # You can change to "mistral" or another local model

# Prompt templates
CLASSIFY_PROMPT = PromptTemplate(
    input_variables=["contract_text"],
    template="""
    Classify this contract. Is it an NDA, SLA, MSA, or Other?\nContract:\n{contract_text}\nType (NDA/SLA/MSA/Other):
    """
)

CLAUSE_PROMPT = PromptTemplate(
    input_variables=["clause_name", "contract_text"],
    template="""
    Extract the *{clause_name}* clause from this contract.\nContract:\n{contract_text}\nClause:
    """
)

RISK_PROMPT = PromptTemplate(
    input_variables=["clause_name", "clause_text"],
    template="""
    Rate the *{clause_name}* clause as Low, Medium, or High risk with 1-sentence justification.\nClause:\n{clause_text}\nRisk (Low/Medium/High) and rationale:
    """
)

SUMMARY_PROMPT = PromptTemplate(
    input_variables=["contract_text"],
    template="""
    Summarize this contract in 2-3 sentences.\nContract:\n{contract_text}\nSummary:
    """
)

KEY_CLAUSES = ["Termination", "Indemnity", "Confidentiality"]

# Helper to extract risk level
def extract_risk_level(risk_text):
    match = re.search(r'\b(Low|Medium|High)\b', risk_text, re.IGNORECASE)
    if match:
        return match.group(1).capitalize()
    return "Unknown"

def analyze_contract(text, doc_id):
    """
    Analyzes a contract: classifies, extracts clauses, scores risk, and summarizes.
    Args:
        text (str): The contract text.
        doc_id (str): Unique identifier for the document.
    Returns:
        dict: {contract_type, clauses, risks, risk_rationales, summary}
    """
    # Use .invoke() for chat models, direct call for Ollama/OpenAI
    def get_llm_response(prompt):
        if LLM_PROVIDER in ["anthropic"]:
            return LLM.invoke(prompt).content.strip()
        else:
            return LLM.invoke(prompt).strip()

    # 1. Classification
    contract_type = get_llm_response(CLASSIFY_PROMPT.format(contract_text=text))
    # 2. Clause extraction
    clauses = {}
    for clause in KEY_CLAUSES:
        clause_text = get_llm_response(CLAUSE_PROMPT.format(clause_name=clause, contract_text=text))
        clauses[clause] = clause_text
    # 3. Risk scoring
    risks = {}
    risk_rationales = {}
    for clause, clause_text in clauses.items():
        risk_response = get_llm_response(RISK_PROMPT.format(clause_name=clause, clause_text=clause_text))
        risk_level = extract_risk_level(risk_response)
        risks[clause] = risk_level
        risk_rationales[clause] = risk_response
    # 4. Summarization
    summary = get_llm_response(SUMMARY_PROMPT.format(contract_text=text))
    return {
        "doc_id": doc_id,
        "contract_type": contract_type,
        "clauses": clauses,
        "risks": risks,
        "risk_rationales": risk_rationales,
        "summary": summary
    } 