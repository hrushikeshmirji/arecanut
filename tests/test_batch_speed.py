import time
import os
import torch
from pathlib import Path
from PIL import Image
from transformers import ViTForImageClassification, ViTImageProcessor

torch.set_num_threads(os.cpu_count() or 4)
WEIGHTS_DIR = Path("D:/arecanut_project/backend/weights/vit_areca_classifier_v2")

processor = ViTImageProcessor.from_pretrained(str(WEIGHTS_DIR))
model = ViTForImageClassification.from_pretrained(str(WEIGHTS_DIR))
model.eval()

sample_dir = Path("D:/arecanut_project/dataset_koleroga/train/images")
sample_files = list(sample_dir.glob("*.jpg"))[:32]

print(f"Testing batch inference on {len(sample_files)} images (batch size 16)...")
t0 = time.time()
with torch.no_grad():
    for i in range(0, len(sample_files), 16):
        batch_files = sample_files[i:i+16]
        images = [Image.open(f).convert("RGB") for f in batch_files]
        inputs = processor(images=images, return_tensors="pt")
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        confs, preds = probs.max(dim=-1)

elapsed = time.time() - t0
print(f"Batch processed {len(sample_files)} images in {elapsed:.2f}s ({elapsed/len(sample_files)*1000:.1f} ms/img)")
