import time
import torch
from pathlib import Path
from PIL import Image
from transformers import ViTForImageClassification, ViTImageProcessor

WEIGHTS_DIR = Path("D:/arecanut_project/backend/weights/vit_areca_classifier_v2")

print("Loading processor and model...")
processor = ViTImageProcessor.from_pretrained(str(WEIGHTS_DIR))
model = ViTForImageClassification.from_pretrained(str(WEIGHTS_DIR))
model.eval()

# Test speed on 10 dummy images or 10 real images
sample_dir = Path("D:/arecanut_project/dataset_koleroga/train/images")
sample_files = list(sample_dir.glob("*.jpg"))[:20]

print(f"Testing inference speed on {len(sample_files)} images...")
t0 = time.time()
with torch.no_grad():
    for f in sample_files:
        im = Image.open(f).convert("RGB")
        inputs = processor(images=im, return_tensors="pt")
        out = model(**inputs)
        probs = torch.nn.functional.softmax(out.logits, dim=-1)
        conf, idx = probs.max(dim=-1)
elapsed = time.time() - t0
print(f"Processed {len(sample_files)} images in {elapsed:.2f}s ({elapsed/len(sample_files)*1000:.1f} ms/img)")
