"""
generate_evaluation_metrics.py
===============================
TASK 4: Comprehensive Model Evaluation & Metric Generation
-----------------------------------------------------------
Evaluates the retrained ViT classifier v3 across all 633 holdout validation
images in D:/arecanut_project/dataset_unified_v3/val/.

Generates:
  1. D:/arecanut_project/evaluation_reports/classification_report.txt
  2. D:/arecanut_project/evaluation_reports/classification_report.json
  3. D:/arecanut_project/evaluation_reports/confusion_matrix.png (300 DPI publication quality)
  4. D:/arecanut_project/evaluation_reports/per_class_metrics_bar.png (300 DPI publication quality)
"""

from __future__ import annotations

import json
import os
import sys
import shutil
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support
from transformers import ViTForImageClassification, ViTImageProcessor

PROJECT_ROOT = Path("D:/arecanut_project").resolve()
VAL_DIR = PROJECT_ROOT / "dataset_unified_v4" / "val"
if not VAL_DIR.exists():
    VAL_DIR = PROJECT_ROOT / "dataset_unified_v3" / "val"

WEIGHTS_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v4"
if not WEIGHTS_DIR.exists():
    WEIGHTS_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v3"

OUTPUT_DIR = PROJECT_ROOT / "evaluation_reports"
REPORT_FIGURES_DIR = PROJECT_ROOT / "report_figures"
BATCH_SIZE = 16


def main():
    print("=" * 80)
    print("  ARECAGUARD: TASK 4 - 9-CLASS COMPREHENSIVE MODEL EVALUATION")
    print("=" * 80)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cpu":
        torch.set_num_threads(min(8, os.cpu_count() or 4))
    print(f"[1] Target Device: {device} (threads: {torch.get_num_threads()})")

    print(f"[2] Loading fine-tuned ViT classifier from {WEIGHTS_DIR}...")
    processor = ViTImageProcessor.from_pretrained(str(WEIGHTS_DIR))
    model = ViTForImageClassification.from_pretrained(str(WEIGHTS_DIR))
    model.to(device)
    model.eval()

    classes = sorted([d.name for d in VAL_DIR.iterdir() if d.is_dir()])
    print(f"[3] Validation Set: {VAL_DIR}")
    print(f"    Discovered {len(classes)} canonical classes: {classes}")

    # Collect images
    all_samples = []
    for cls_name in classes:
        cls_folder = VAL_DIR / cls_name
        files = [
            p for p in cls_folder.iterdir()
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        ]
        for f in files:
            all_samples.append((f, cls_name))

    print(f"[4] Evaluating {len(all_samples)} validation samples (batch size {BATCH_SIZE})...")

    y_true_list = []
    y_pred_list = []
    confidences = []

    with torch.no_grad():
        for i in range(0, len(all_samples), BATCH_SIZE):
            batch = all_samples[i:i + BATCH_SIZE]
            imgs = [Image.open(p).convert("RGB") for p, _ in batch]
            inputs = processor(images=imgs, return_tensors="pt").to(device)
            outputs = model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            confs, preds = probs.max(dim=-1)

            for j, (p, true_cls) in enumerate(batch):
                pred_label = model.config.id2label[preds[j].item()]
                y_true_list.append(true_cls)
                y_pred_list.append(pred_label)
                confidences.append(float(confs[j].item()))

    total_imgs = len(y_true_list)
    accuracy = (sum(1 for yt, yp in zip(y_true_list, y_pred_list) if yt == yp) / total_imgs) * 100.0
    print(f"    Evaluated {total_imgs} images. Overall Accuracy: {accuracy:.2f}%")

    # ── 1. Classification Report ─────────────────────────────────────────────
    report_dict = classification_report(
        y_true_list,
        y_pred_list,
        target_names=classes,
        labels=classes,
        output_dict=True,
        zero_division=0,
    )
    report_text = classification_report(
        y_true_list,
        y_pred_list,
        target_names=classes,
        labels=classes,
        digits=4,
        zero_division=0,
    )

    report_txt_path = OUTPUT_DIR / "classification_report.txt"
    with open(report_txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("  ARECAGUARD 9-CLASS ViT CLASSIFIER (V3 RETRAINED) EVALUATION REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(report_text + "\n\n")
        f.write(f"Overall Accuracy          : {accuracy:.2f}%\n")
        f.write(f"Macro F1-Score            : {report_dict['macro avg']['f1-score']*100:.2f}%\n")
        f.write(f"Weighted F1-Score         : {report_dict['weighted avg']['f1-score']*100:.2f}%\n")
        f.write(f"Mean Prediction Confidence: {np.mean(confidences)*100:.2f}%\n")
        f.write(f"Total Validation Samples  : {total_imgs}\n")

    report_json_path = OUTPUT_DIR / "classification_report.json"
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "overall_accuracy": round(accuracy, 2),
            "macro_f1": round(report_dict["macro avg"]["f1-score"] * 100.0, 2),
            "weighted_f1": round(report_dict["weighted avg"]["f1-score"] * 100.0, 2),
            "mean_confidence": round(float(np.mean(confidences) * 100.0), 2),
            "total_samples": total_imgs,
            "metrics_per_class": {
                c: {
                    "precision": round(report_dict[c]["precision"] * 100.0, 2),
                    "recall": round(report_dict[c]["recall"] * 100.0, 2),
                    "f1_score": round(report_dict[c]["f1-score"] * 100.0, 2),
                    "support": int(report_dict[c]["support"])
                }
                for c in classes
            }
        }, f, indent=2)

    print(f"\n[5] Classification Report:\n{report_text}")

    # ── 2. Confusion Matrix Heatmap (300 DPI) ─────────────────────────────────
    cm = confusion_matrix(y_true_list, y_pred_list, labels=classes)
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)

    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.set_ylabel("Validation Sample Count", rotation=-90, va="bottom", fontsize=10)

    # Format ticks
    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=classes,
        yticklabels=classes,
        title=f"ArecaGuard 9-Class Confusion Matrix (Acc: {accuracy:.2f}%, N={total_imgs})",
        ylabel="Ground Truth Class",
        xlabel="Predicted Class",
    )
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Annotate numbers in cells
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            ax.text(
                j,
                i,
                f"{val}",
                ha="center",
                va="center",
                color="white" if val > thresh else "black",
                fontweight="bold" if val > 0 else "normal",
                fontsize=9,
            )

    fig.tight_layout()
    cm_path = OUTPUT_DIR / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=300, bbox_inches="tight")
    # Also save to report_figures for documentation
    shutil.copy2(cm_path, REPORT_FIGURES_DIR / "Fig_4_3_stage_3_confusion_matrix.png")
    plt.close(fig)
    print(f"[6] Saved Confusion Matrix Plot (300 DPI) -> {cm_path}")

    # ── 3. Per-Class Metrics Bar Chart (300 DPI) ──────────────────────────────
    prec, rec, f1, support = precision_recall_fscore_support(
        y_true_list,
        y_pred_list,
        labels=classes,
        zero_division=0,
    )

    x = np.arange(len(classes))
    width = 0.26

    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    rects1 = ax.bar(x - width, prec * 100, width, label="Precision", color="#1f77b4")
    rects2 = ax.bar(x, rec * 100, width, label="Recall", color="#2ca02c")
    rects3 = ax.bar(x + width, f1 * 100, width, label="F1-Score", color="#ff7f0e")

    ax.set_ylabel("Score (%)", fontsize=11)
    ax.set_title(f"ArecaGuard 9-Class Performance Metrics (Macro F1: {report_dict['macro avg']['f1-score']*100:.2f}%)", fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(classes, rotation=35, ha="right", fontsize=9)
    ax.set_ylim(0, 115)
    ax.legend(loc="upper right", frameon=True)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(
                f"{height:.1f}%",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=7,
                rotation=45,
            )

    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)

    fig.tight_layout()
    bar_path = OUTPUT_DIR / "per_class_metrics_bar.png"
    plt.savefig(bar_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[7] Saved Per-Class Metrics Bar Chart (300 DPI) -> {bar_path}")

    print("\n" + "=" * 80)
    print("  TASK 4: MODEL EVALUATION & METRIC GENERATION COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    main()
