import os
import requests
import zipfile
import json
from tqdm import tqdm

CUAD_URL = "https://github.com/TheAtticusProject/cuad/archive/refs/heads/master.zip"
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'uploads')
CUAD_ZIP = os.path.join(DATA_DIR, 'cuad.zip')
CUAD_EXTRACTED = os.path.join(DATA_DIR, 'cuad-main')

os.makedirs(DATA_DIR, exist_ok=True)

def download_cuad():
    print("Downloading CUAD dataset...")
    r = requests.get(CUAD_URL, stream=True)
    with open(CUAD_ZIP, 'wb') as f:
        for chunk in tqdm(r.iter_content(chunk_size=8192)):
            if chunk:
                f.write(chunk)
    print("Download complete.")

def extract_zip():
    print("Extracting CUAD zip...")
    with zipfile.ZipFile(CUAD_ZIP, 'r') as zip_ref:
        zip_ref.extractall(DATA_DIR)
    print("Extraction complete.")

def process_contracts():
    print("Processing contracts and labels from CUADv1.json...")
    contracts_json = os.path.join(CUAD_EXTRACTED, 'CUADv1.json')
    data_zip = os.path.join(CUAD_EXTRACTED, 'data.zip')
    # If CUADv1.json is missing, extract data.zip
    if not os.path.exists(contracts_json):
        print("CUADv1.json not found, extracting data.zip...")
        with zipfile.ZipFile(data_zip, 'r') as zip_ref:
            zip_ref.extractall(CUAD_EXTRACTED)
    with open(contracts_json, 'r') as f:
        data = json.load(f)
    # CUADv1.json is a dict with a 'data' key containing a list of contracts
    for entry in tqdm(data["data"]):
        contract_name = entry.get('title', f"contract_{data['data'].index(entry)}.txt")
        contract_text = "\n\n".join([p.get('context', '') for p in entry.get('paragraphs', [])])
        contract_labels = entry.get('paragraphs', [])
        if contract_text:
            out_txt = os.path.join(DATA_DIR, contract_name if contract_name.endswith('.txt') else contract_name + '.txt')
            with open(out_txt, 'w') as outf:
                outf.write(contract_text)
            out_json = out_txt.replace('.txt', '.json')
            with open(out_json, 'w') as jf:
                json.dump(contract_labels, jf, indent=2)
    print("Contracts and labels processed.")

def main():
    if not os.path.exists(CUAD_ZIP):
        download_cuad()
    if not os.path.exists(CUAD_EXTRACTED):
        extract_zip()
    process_contracts()
    print(f"Done! Check {DATA_DIR} for contracts and labels.")

if __name__ == "__main__":
    main() 