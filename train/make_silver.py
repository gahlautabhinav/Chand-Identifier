# train/make_silver.py
import json, sys, argparse, os
from scripts.pipeline import infer_line, syllabify_devanagari, silver_label_syllable
from pathlib import Path
from scripts.utils import normalize_text

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def process_lines(input_txt, out_jsonl, use_sandhi=True):
    out = []
    with open(input_txt, 'r', encoding='utf-8') as f:
        lines = [normalize_text(x) for x in f if x.strip()]
    for i, line in enumerate(lines):
        res = infer_line(line, use_sandhi=use_sandhi)
        chosen = res['chosen_candidate']
        syllables = chosen['syllables']
        labels = chosen['silver_labels']
        # normalize label tokens to 'L'/'G'
        rec = {"id": i, "text": line, "syllables": syllables, "labels": labels}
        out.append(rec)
    # write jsonl
    p = Path(out_jsonl)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8') as fo:
        for r in out:
            fo.write(json.dumps(r, ensure_ascii=False) + '\n')
    print(f"Wrote {len(out)} records to {out_jsonl}")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True, help='text file (one line per row)')
    ap.add_argument('--out', default='train/hf_silver.jsonl')
    ap.add_argument('--nosandhi', action='store_true')
    args = ap.parse_args()
    process_lines(args.input, args.out, use_sandhi=not args.nosandhi)
