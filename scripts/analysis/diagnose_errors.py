import torch
from pathlib import Path
from PIL import Image
from transformers import ViTForImageClassification, ViTImageProcessor

WEIGHTS_DIR = Path("backend/weights/vit_areca_classifier_v3")
VAL_DIR = Path("dataset_unified_v3/val")

processor = ViTImageProcessor.from_pretrained(str(WEIGHTS_DIR))
model = ViTForImageClassification.from_pretrained(str(WEIGHTS_DIR))
model.eval()

errors = []
for cls_folder in sorted(VAL_DIR.iterdir()):
    if not cls_folder.is_dir():
        continue
    true_cls = cls_folder.name
    for img_p in sorted(cls_folder.glob("*.*")):
        with Image.open(img_p) as raw:
            im = raw.convert("RGB")
            inputs = processor(images=im, return_tensors="pt")
        with torch.no_grad():
            out = model(**inputs)
            prob = torch.nn.functional.softmax(out.logits, dim=-1)
            conf, pred = prob.max(dim=-1)
            pred_cls = model.config.id2label[pred.item()]
        if pred_cls != true_cls:
            errors.append({
                "file": img_p.name,
                "path": str(img_p),
                "true": true_cls,
                "pred": pred_cls,
                "conf": round(conf.item() * 100, 2),
                "true_conf": round(prob[0, model.config.label2id[true_cls]].item() * 100, 2)
            })

print(f"Total misclassifications: {len(errors)} / 633 validation samples")
for e in errors:
    print(f"  {e['file']} | True: {e['true']} ({e['true_conf']}%) -> Pred: {e['pred']} ({e['conf']}%)")
