# train/export_for_annotation.py
import json
import csv
import argparse
from pathlib import Path

def export(jsonl_path: str, out_csv: str):
    rows = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            rows.append({
                'id': r.get('id', ''),
                'text': r.get('text', ''),
                'syllables': '|'.join(r.get('syllables', [])),
                'labels': '|'.join(r.get('labels', [])),
            })
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, 'w', encoding='utf-8', newline='') as fo:
        writer = csv.DictWriter(fo, fieldnames=['id', 'text', 'syllables', 'labels'])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"Exported {len(rows)} rows to {out_csv}")

def main():
    ap = argparse.ArgumentParser(description='Export HF JSONL to CSV for annotators')
    ap.add_argument('jsonl', help='input jsonl file (hf_silver.jsonl)')
    ap.add_argument('outcsv', help='output CSV path')
    args = ap.parse_args()
    export(args.jsonl, args.outcsv)

if __name__ == '__main__':
    main()
