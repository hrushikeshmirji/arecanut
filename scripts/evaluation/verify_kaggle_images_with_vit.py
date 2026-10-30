import os
import sys
import torch
from PIL import Image
from torchvision import transforms
from transformers import ViTForImageClassification

# Set stdout encoding
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_DIR = r"D:\arecanut_project\backend\weights\vit_areca_classifier_v3"

print(f"Loading ViT model from: {MODEL_DIR} on {DEVICE}")
model = ViTForImageClassification.from_pretrained(MODEL_DIR).to(DEVICE)
model.eval()

id2label = model.config.id2label
print(f"Model labels: {id2label}")

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def evaluate_folder(folder_path, max_samples=100):
    counts = {}
    total = 0
    high_conf = 0
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    sample_files = files[:max_samples]
    
    with torch.no_grad():
        for f in sample_files:
            p = os.path.join(folder_path, f)
            try:
                img = Image.open(p).convert("RGB")
                tensor = transform(img).unsqueeze(0).to(DEVICE)
                logits = model(tensor).logits
                probs = torch.softmax(logits, dim=-1)[0]
                pred_idx = torch.argmax(probs).item()
                pred_label = id2label[pred_idx]
                conf = probs[pred_idx].item()
                
                counts[pred_label] = counts.get(pred_label, 0) + 1
                total += 1
                if conf >= 0.85:
                    high_conf += 1
            except Exception as e:
                pass
    return counts, total, high_conf

print("\n--- Testing Kannadapranesh Arecanut_YellowBrownSpot (sample of 100) ---")
spot_dir = r"C:\Users\Hrushikesh Mirji\.cache\kagglehub\datasets\kannadapranesh\coconut-and-arecanut-diseases\versions\1\archive\Arecanut_YellowBrownSpot\Arecanut_YellowBrownSpot"
c, t, hc = evaluate_folder(spot_dir, max_samples=100)
print(f"Classified {t} samples (High conf >= 85%: {hc}/{t}): {c}")

print("\n--- Testing Kannadapranesh Healthy_Leaves (sample of 100) ---")
healthy_dir = r"C:\Users\Hrushikesh Mirji\.cache\kagglehub\datasets\kannadapranesh\coconut-and-arecanut-diseases\versions\1\archive\Healthy_Leaves\Healthy_Leaves"
c, t, hc = evaluate_folder(healthy_dir, max_samples=100)
print(f"Classified {t} samples (High conf >= 85%: {hc}/{t}): {c}")

print("\n--- Testing Kannadapranesh Coconut WCLWD_DryingofLeaflets (sample of 50) ---")
coco_dir = r"C:\Users\Hrushikesh Mirji\.cache\kagglehub\datasets\kannadapranesh\coconut-and-arecanut-diseases\versions\1\archive\WCLWD_DryingofLeaflets\WCLWD_DryingofLeaflets"
c, t, hc = evaluate_folder(coco_dir, max_samples=50)
print(f"Classified {t} samples: {c}")
