import os
import json

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'prompts')
os.makedirs(PROMPTS_DIR, exist_ok=True)

PROMPT_EXAMPLES = {
    "clause_extraction": [
        {
            "input": "Extract the Indemnity clause from the following contract text: ...",
            "output": "Indemnity: The parties agree to..."
        },
        {
            "input": "Extract the Termination clause from the following contract text: ...",
            "output": "Termination: This agreement may be terminated if..."
        }
    ],
    "risk_scoring": [
        {
            "input": "Rate this clause from Low to High risk with explanation: 'The party may terminate at any time.'",
            "output": "High risk: The clause allows termination at any time without cause, which is risky for the counterparty."
        }
    ],
    "contract_classification": [
        {
            "input": "Classify this document: 'This Non-Disclosure Agreement (NDA) is made between...'",
            "output": "NDA"
        },
        {
            "input": "Classify this document: 'This Service Level Agreement (SLA) sets forth...'",
            "output": "SLA"
        }
    ]
}

def main():
    out_path = os.path.join(PROMPTS_DIR, 'prompt_examples.json')
    with open(out_path, 'w') as f:
        json.dump(PROMPT_EXAMPLES, f, indent=2)
    print(f"Prompt examples written to {out_path}")

if __name__ == "__main__":
    main() 