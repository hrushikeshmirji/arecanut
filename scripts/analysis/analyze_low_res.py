import os
import io
import zipfile
from pathlib import Path
from PIL import Image
import numpy as np

# Let's inspect where the low_resolution candidates came from and their dimension distribution
PROJECT_ROOT = Path("D:/arecanut_project").resolve()
patches_dir = PROJECT_ROOT / "dataset_patches"

low_res_list = []

# Scan dataset_patches
if patches_dir.exists():
    for p in patches_dir.rglob("*.*"):
        if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            try:
                with Image.open(p) as im:
                    w, h = im.size
                    if w < 224 or h < 224:
                        low_res_list.append({
                            "source": "dataset_patches",
                            "path": p,
                            "size": (w, h),
                            "min_dim": min(w, h),
                            "max_dim": max(w, h),
                            "area": w * h
                        })
            except Exception:
                pass

print(f"Total low-res in dataset_patches: {len(low_res_list)}")

# Distribution of min_dim
bins = [0, 50, 100, 150, 180, 200, 224]
counts = {f"{bins[i]}-{bins[i+1]}px": 0 for i in range(len(bins)-1)}

for item in low_res_list:
    m = item["min_dim"]
    for i in range(len(bins)-1):
        if bins[i] <= m < bins[i+1]:
            counts[f"{bins[i]}-{bins[i+1]}px"] += 1
            break

print("\nResolution Distribution of Rejected Sub-224px Images:")
for k, v in counts.items():
    print(f"  {k:<15}: {v} images")

