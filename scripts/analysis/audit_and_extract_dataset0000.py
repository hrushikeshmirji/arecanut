"""
audit_and_extract_dataset0000.py
=================================
Scans the 3,852 new images from C:/Users/Hrushikesh Mirji/Downloads/dataset0000.zip:
  - areca_diseased_phytoplasma_yellow_leaf
  - areca_diseased_physiological_nut_cracking
  - areca_healthy
  - areca_diseased_fungal_fruit_rot
  - non_areca
Audits:
  1. Resolution (>= 224x224 px)
  2. Variance (>= 15.0)
  3. Deduplication against dataset_unified_v3 (3,147 hashes)
  4. ViT Self-Classification confidence distribution
"""

import io
import json
import hashlib
import zipfile
from pathlib import Path
from PIL import Image
import numpy as np
import torch
from transformers import ViTForImageClassification, ViTImageProcessor

PROJECT_ROOT = Path("D:/arecanut_project").resolve()
UNIFIED_DIR = PROJECT_ROOT / "dataset_unified_v3"
WEIGHTS_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v3"
ZIP_PATH = Path(r"C:\Users\Hrushikesh Mirji\Downloads\dataset0000.zip")

# Load existing hashes
print("[1] Loading existing hashes from dataset_unified_v3...")
existing_hashes = set()
for p in UNIFIED_DIR.rglob("*.*"):
    if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
        with open(p, "rb") as f:
            existing_hashes.add(hashlib.md5(f.read()).hexdigest())
print(f"    Indexed {len(existing_hashes)} active hashes.")

# Categories of interest
CATEGORIES = [
    "areca_diseased_phytoplasma_yellow_leaf",
    "areca_diseased_physiological_nut_cracking",
    "areca_healthy",
    "areca_diseased_fungal_fruit_rot",
    "non_areca",
]

print(f"\n[2] Scanning {ZIP_PATH.name} for categories: {CATEGORIES}...")
candidates = []
with zipfile.ZipFile(ZIP_PATH, "r") as z:
    for n in z.namelist():
        if not n.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        parts = n.split("/")
        if len(parts) >= 4 and parts[0] == "dataset" and parts[1] == "dataset" and parts[2] in ["train", "validation"]:
            cat = parts[3]
            if cat in CATEGORIES:
                data = z.read(n)
                h = hashlib.md5(data).hexdigest()
                if h in existing_hashes:
                    continue
                candidates.append({
                    "zip_entry": n,
                    "cat": cat,
                    "md5": h,
                    "size_bytes": len(data)
                })

print(f"    Found {len(candidates)} new unique candidates across target categories.")
cat_counts = {}
for c in candidates:
    cat_counts[c["cat"]] = cat_counts.get(c["cat"], 0) + 1
for k, v in sorted(cat_counts.items()):
    print(f"      - {k:<45}: {v}")

# Test 50 samples with ViT to inspect self-classification agreement
print("\n[3] Testing sample self-classification agreement with ViT-v3...")
processor = ViTImageProcessor.from_pretrained(str(WEIGHTS_DIR))
model = ViTForImageClassification.from_pretrained(str(WEIGHTS_DIR))
model.eval()

sample_candidates = candidates[:50]
passed_gates = 0
with zipfile.ZipFile(ZIP_PATH, "r") as z:
    for cand in sample_candidates:
        data = z.read(cand["zip_entry"])
        try:
            im = Image.open(io.BytesIO(data)).convert("RGB")
            w, h = im.size
            if w < 224 or h < 224:
                continue
            gray = im.convert("L")
            var = float(np.var(np.array(gray, dtype=np.float32)))
            if var < 15.0:
                continue

            inp = processor(images=im, return_tensors="pt")
            with torch.no_grad():
                out = model(**inp)
                prob = torch.nn.functional.softmax(out.logits, dim=-1)
                conf, pred = prob.max(dim=-1)
                pred_label = model.config.id2label[pred.item()]

            passed_gates += 1
            cand["pred"] = pred_label
            cand["conf"] = round(conf.item() * 100, 1)
            cand["dim"] = (w, h)
        except Exception:
            pass

print(f"    Evaluated 50 samples: {passed_gates} passed Gates 1-4.")
print("    Sample classifications:")
for cand in [c for c in sample_candidates if "pred" in c][:10]:
    print(f"      Source: {cand['cat'][:30]:<30} -> ViT Pred: {cand['pred']:<15} (Conf: {cand['conf']}%, Size: {cand['dim']})")
