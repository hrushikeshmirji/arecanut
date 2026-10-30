import sys
import torch
from pathlib import Path
from PIL import Image
from torchvision import transforms
from transformers import ViTForImageClassification, ViTImageProcessor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

WEIGHTS_DIR = Path("backend/weights/vit_areca_classifier_v3")
VAL_DIR = Path("dataset_unified_v3/val")

processor = ViTImageProcessor.from_pretrained(str(WEIGHTS_DIR))
model = ViTForImageClassification.from_pretrained(str(WEIGHTS_DIR))
model.eval()

device = torch.device("cpu")

# Load all 633 validation samples
samples = []
for c_dir in sorted(VAL_DIR.iterdir()):
    if not c_dir.is_dir():
        continue
    c_name = c_dir.name
    for f in sorted(c_dir.glob("*.*")):
        samples.append((f, c_name))

print(f"Loaded {len(samples)} validation samples across 9 classes.")

# 1. Standard Accuracy
std_correct = 0
# 2. TTA (Test-Time Augmentation: Original + Horizontal Flip)
tta_correct = 0
# 3. Pathology-Sensitive Gating
gated_correct = 0

fruit_rot_idx = model.config.label2id["fruit_rot"]
healthy_nut_idx = model.config.label2id["healthy_nut"]

with torch.no_grad():
    for f, true_cls in samples:
        im = Image.open(f).convert("RGB")
        im_flip = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

        # Standard forward pass
        inp = processor(images=im, return_tensors="pt").to(device)
        out = model(**inp)
        probs_std = torch.nn.functional.softmax(out.logits, dim=-1)[0]
        pred_std = model.config.id2label[probs_std.argmax().item()]

        if pred_std == true_cls:
            std_correct += 1

        # TTA forward pass
        inp_flip = processor(images=im_flip, return_tensors="pt").to(device)
        out_flip = model(**inp_flip)
        probs_flip = torch.nn.functional.softmax(out_flip.logits, dim=-1)[0]
        probs_tta = (probs_std + probs_flip) / 2.0
        pred_tta = model.config.id2label[probs_tta.argmax().item()]

        if pred_tta == true_cls:
            tta_correct += 1

        # Pathology-Sensitive Decision Gating:
        # If disease symptoms (fruit_rot) are actively detected (>30%) and competing with healthy_nut within 10%,
        # prioritize disease detection to prevent dangerous agricultural false negatives.
        probs_gated = probs_tta.clone()
        p_rot = probs_gated[fruit_rot_idx].item()
        p_nut = probs_gated[healthy_nut_idx].item()

        if p_rot > 0.30 and (p_nut - p_rot) < 0.10:
            probs_gated[fruit_rot_idx] += 0.12

        pred_gated = model.config.id2label[probs_gated.argmax().item()]
        if pred_gated == true_cls:
            gated_correct += 1

n = len(samples)
print("\n" + "=" * 70)
print("  ML MODEL ACCURACY COMPARISON ACROSS IMPROVISATIONS")
print("=" * 70)
print(f"1. Standard Single-Pass ViT      : {(std_correct/n)*100:.2f}% ({std_correct}/{n})")
print(f"2. Test-Time Augmentation (TTA)  : {(tta_correct/n)*100:.2f}% ({tta_correct}/{n})")
print(f"3. Pathology-Sensitive Gating   : {(gated_correct/n)*100:.2f}% ({gated_correct}/{n})")
print("=" * 70)
