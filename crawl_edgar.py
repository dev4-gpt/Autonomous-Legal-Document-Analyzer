import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'uploads')
os.makedirs(DATA_DIR, exist_ok=True)

SEARCH_URL = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=&type=10-K&dateb=&owner=exclude&count=10"
BASE_URL = "https://www.sec.gov"

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; AutonomousLegalAnalyzer/1.0)'}

def fetch_recent_filings():
    print("Fetching recent 10-K filings from EDGAR...")
    r = requests.get(SEARCH_URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    links = [BASE_URL + a['href'] for a in soup.find_all('a', href=True) if 'Archives/edgar/data' in a['href']]
    return links[:5]  # Limit for demo

def fetch_and_save_documents(filing_links):
    for link in tqdm(filing_links):
        r = requests.get(link, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        doc_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.txt')]
        for doc_link in doc_links[:1]:  # Only first doc per filing
            doc_url = BASE_URL + doc_link
            doc_resp = requests.get(doc_url, headers=HEADERS)
            # Clean filename
            fname = re.sub(r'[^a-zA-Z0-9]', '_', doc_link.split('/')[-1])
            out_path = os.path.join(DATA_DIR, f'edgar_{fname}')
            with open(out_path, 'w') as f:
                f.write(doc_resp.text)
            print(f"Saved {out_path}")

def main():
    links = fetch_recent_filings()
    fetch_and_save_documents(links)
    print(f"Done! Check {DATA_DIR} for EDGAR contracts.")

if __name__ == "__main__":
    main() 