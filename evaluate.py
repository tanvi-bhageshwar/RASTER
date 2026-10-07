"""Batch run: python evaluate.py logos/  -> results.csv"""
import sys, glob, csv, os
from PIL import Image
from vectorise import load_rgb_on_white, trace, evaluate

folder = sys.argv[1] if len(sys.argv) > 1 else "logos"
rows = []
for f in sorted(glob.glob(os.path.join(folder, "*.*"))):
    try:
        orig = load_rgb_on_white(Image.open(f))
        stats, _ = evaluate(orig, trace(orig))
        rows.append({"file": os.path.basename(f), **stats})
        print(rows[-1])
    except Exception as e:
        print("FAILED", f, e)
if rows:
    with open("results.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
