import torch
from pathlib import Path
from PIL import Image
from transformers import ViTForImageClassification, ViTImageProcessor

WEIGHTS_DIR = Path("D:/arecanut_project/backend/weights/vit_areca_classifier_v2")
processor = ViTImageProcessor.from_pretrained(str(WEIGHTS_DIR))
model = ViTForImageClassification.from_pretrained(str(WEIGHTS_DIR))
model.eval()

patches_dir = Path("D:/arecanut_project/dataset_patches")

# Collect images with min_dim >= 150 and < 224
candidates = []
for p in patches_dir.rglob("*.*"):
    if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
        try:
            with Image.open(p) as im:
                w, h = im.size
                if 160 <= min(w, h) < 224:
                    candidates.append((p, (w, h)))
        except Exception:
            pass

print(f"Total candidates in 160-223px range: {len(candidates)}")

# Test on 30 sample images with Lanczos upscaling to 224x224
print("Testing Lanczos upscaling and ViT inference on sample 30 images...")
results = []
with torch.no_grad():
    for p, orig_size in candidates[:30]:
        im = Image.open(p).convert("RGB")
        # Upscale with Lanczos
        im_upscaled = im.resize((224, 224), Image.Resampling.LANCZOS)
        inputs = processor(images=im_upscaled, return_tensors="pt")
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        conf, pred = probs.max(dim=-1)
        label = model.config.id2label[pred.item()]
        results.append({
            "file": p.name,
            "orig_size": orig_size,
            "pred": label,
            "conf": conf.item() * 100.0
        })

high_conf = [r for r in results if r["conf"] >= 85.0]
print(f"Passed >= 85% confidence: {len(high_conf)} / {len(results)} ({len(high_conf)/len(results)*100:.1f}%)")
print("\nSample predictions on upscaled 160-223px images:")
for r in results[:10]:
    print(f"  {r['file']:<35} Orig: {str(r['orig_size']):<12} -> Pred: {r['pred']:<15} Conf: {r['conf']:.1f}%")
