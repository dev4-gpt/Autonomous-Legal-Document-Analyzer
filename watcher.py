import time
import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from parser import parse_contract, SUPPORTED_EXTENSIONS
from embedder import chunk_and_embed
from agent import analyze_contract

data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'uploads')
analysis_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'analysis')
os.makedirs(analysis_dir, exist_ok=True)

class ContractHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        ext = os.path.splitext(event.src_path)[1].lower()
        if ext in SUPPORTED_EXTENSIONS:
            print(f"New contract detected: {event.src_path}")
            try:
                text = parse_contract(event.src_path)
                print(f"Extracted text (first 200 chars):\n{text[:200]}\n---")
                chunk_and_embed(text, os.path.basename(event.src_path))
                # Analyze and save results
                analysis = analyze_contract(text, os.path.basename(event.src_path))
                out_json = os.path.join(analysis_dir, os.path.basename(event.src_path) + '.json')
                with open(out_json, 'w') as f:
                    json.dump(analysis, f, indent=2)
                print(f"Analysis saved to {out_json}")
            except Exception as e:
                print(f"Failed to process {event.src_path}: {e}")

def main():
    print(f"Watching {data_dir} for new contracts...")
    event_handler = ContractHandler()
    observer = Observer()
    observer.schedule(event_handler, data_dir, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main() 