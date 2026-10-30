from pathlib import Path
from PIL import Image
import json

out_dir = Path("dataset_legacy_sanitized")
manifest_path = out_dir / "manifest.json"
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = json.load(f)

print(f"Total in manifest: {len(manifest)}")

classes = {}
for item in manifest:
    c = item["class"]
    classes[c] = classes.get(c, 0) + 1

for c, count in sorted(classes.items()):
    folder = out_dir / c
    actual_files = list(folder.glob("*.jpg"))
    print(f"Class {c:<15}: manifest={count:<5} actual_files={len(actual_files)}")

print("\nSample image details (first 5):")
for item in manifest[:5]:
    p = out_dir / item["class"] / item["filename"]
    with Image.open(p) as im:
        print(f"  {item['filename']} -> Class: {item['class']}, Conf: {item['confidence']*100:.1f}%, Size: {im.size}, Repo: {item['original_repo']}")

print("\nSample image details (fruit_rot samples):")
fruit_rot_samples = [it for it in manifest if it["class"] == "fruit_rot"][:5]
for item in fruit_rot_samples:
    p = out_dir / item["class"] / item["filename"]
    with Image.open(p) as im:
        print(f"  {item['filename']} -> Class: {item['class']}, Conf: {item['confidence']*100:.1f}%, Size: {im.size}, Repo: {item['original_repo']}")
