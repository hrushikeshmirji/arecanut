import os
import yaml
from PIL import Image

DATASET_DIR = r"D:\arecanut_project\dataset_koleroga"
YAML_PATH = os.path.join(DATASET_DIR, "data.yaml")
OUTPUT_DIR = r"D:\arecanut_project\dataset_patches\fruit_rot"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Read class names from data.yaml
with open(YAML_PATH, "r") as f:
    data_cfg = yaml.safe_load(f)

names = data_cfg.get("names", [])
if isinstance(names, dict):
    names = [names[i] for i in sorted(names.keys())]

print(f"Detected classes in dataset: {names}")

# Locate index for mahali / fruit rot
target_idx = None
for idx, name in enumerate(names):
    if "mahali" in name.lower() or "koleroga" in name.lower() or "fruit" in name.lower():
        target_idx = idx
        print(f"Targeting class '{name}' at index {target_idx}")
        break

if target_idx is None:
    raise ValueError(f"Could not find a Mahali/Koleroga class in: {names}")

# 2. Iterate through splits and crop patches
splits = ["train", "valid", "test"]
saved_count = 0

for split in splits:
    img_dir = os.path.join(DATASET_DIR, split, "images")
    lbl_dir = os.path.join(DATASET_DIR, split, "labels")

    if not os.path.exists(img_dir) or not os.path.exists(lbl_dir):
        continue

    for lbl_file in os.listdir(lbl_dir):
        if not lbl_file.endswith(".txt"):
            continue

        lbl_path = os.path.join(lbl_dir, lbl_file)
        base_name = os.path.splitext(lbl_file)[0]

        # Find corresponding image
        img_path = None
        for ext in [".jpg", ".jpeg", ".png", ".JPG"]:
            candidate = os.path.join(img_dir, base_name + ext)
            if os.path.exists(candidate):
                img_path = candidate
                break

        if not img_path:
            continue

        with open(lbl_path, "r") as f:
            lines = f.readlines()

        # Check if file has target annotations
        target_boxes = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 5 and int(parts[0]) == target_idx:
                target_boxes.append([float(p) for p in parts[1:5]])

        if not target_boxes:
            continue

        try:
            with Image.open(img_path).convert("RGB") as img:
                w, h = img.size
                for i, (xc, yc, bw, bh) in enumerate(target_boxes):
                    x1 = max(0, int((xc - bw / 2) * w))
                    y1 = max(0, int((yc - bh / 2) * h))
                    x2 = min(w, int((xc + bw / 2) * w))
                    y2 = min(h, int((yc + bh / 2) * h))

                    # Filter out degenerate boxes
                    if (x2 - x1) >= 20 and (y2 - y1) >= 20:
                        crop = img.crop((x1, y1, x2, y2))
                        crop_name = f"{split}_{base_name}_crop{i}.jpg"
                        crop.save(os.path.join(OUTPUT_DIR, crop_name), quality=95)
                        saved_count += 1
        except Exception as e:
            print(f"Skipping {img_path}: {e}")

print(f"\nDone! Extracted {saved_count} verified Fruit Rot lesion patches to:")
print(f"-> {OUTPUT_DIR}")
