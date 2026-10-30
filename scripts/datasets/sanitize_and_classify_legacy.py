"""
sanitize_and_classify_legacy.py
================================
Automated, high-fidelity sanitization, self-classification, and renaming pipeline
for legacy arecanut dataset collections.

Enforces 5 Strict Quality Gates:
  1. Integrity & Decodability (PIL RGB decode, corruption check)
  2. Resolution & Aspect Ratio (min 224x224 px, aspect 0.25-4.0, downscale if >1024px with Lanczos, NO upscaling)
  3. Texture & Information Density (Grayscale pixel variance >= 15.0)
  4. Cryptographic Deduplication (MD5 hash check against active dataset and within run)
  5. AI Self-Classification (Fine-tuned ViT-B/16 model, confidence threshold >= 85.0%)

Outputs cleanly organized canonical folders in:
  D:/arecanut_project/dataset_legacy_sanitized/<canonical_class>/
  With standardized names: <class>_leg_0001.jpg
"""

import os
import sys
import io
import json
import time
import hashlib
import zipfile
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import numpy as np
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

import torch
from transformers import ViTForImageClassification, ViTImageProcessor

# ── Paths & Setup ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path("D:/arecanut_project").resolve()
ACTIVE_DATASET = PROJECT_ROOT / "dataset_large_scale_verified"
OUTPUT_ROOT = PROJECT_ROOT / "dataset_legacy_sanitized"
WEIGHTS_DIR = PROJECT_ROOT / "backend" / "weights" / "vit_areca_classifier_v2"

CANONICAL_CLASSES = [
    "bud_borer",
    "fruit_rot",
    "healthy_leaf",
    "healthy_nut",
    "healthy_trunk",
    "non_areca",
    "stem_bleeding",
    "stem_cracking",
    "yellow_leaf",
]

CONFIDENCE_THRESHOLD = 0.85  # 85.0% strict cutoff
BATCH_SIZE = 16
MAX_DIM = 1024
MIN_DIM = 224
MIN_VARIANCE = 15.0

torch.set_num_threads(os.cpu_count() or 4)


def compute_md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def check_variance(img: Image.Image) -> float:
    gray = img.convert("L")
    arr = np.array(gray, dtype=np.float32)
    return float(np.var(arr))


def normalize_image(img: Image.Image) -> Image.Image:
    """Downscale proportionally if > MAX_DIM using high-fidelity LANCZOS; never upscale."""
    w, h = img.size
    if max(w, h) > MAX_DIM:
        if w >= h:
            new_w = MAX_DIM
            new_h = max(MIN_DIM, int(h * (MAX_DIM / w)))
        else:
            new_h = MAX_DIM
            new_w = max(MIN_DIM, int(w * (MAX_DIM / h)))
        return img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    return img


def load_active_hashes() -> Set[str]:
    print("[1] Indexing active verified dataset hashes...")
    hashes = set()
    if ACTIVE_DATASET.exists():
        for p in ACTIVE_DATASET.rglob("*.*"):
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
                try:
                    with open(p, "rb") as f:
                        hashes.add(compute_md5(f.read()))
                except Exception:
                    pass
    print(f"    Indexed {len(hashes)} existing active hashes.")
    return hashes


def collect_candidate_sources() -> List[Dict]:
    """
    Gathers image candidates from legacy directories and zip archives.
    Returns metadata list: {'source_type': 'file'|'zip', 'path': Path, 'subpath': str, 'name': str}
    """
    print("\n[2] Scanning candidate legacy repositories...")
    candidates = []

    # 1. dataset_koleroga
    koleroga_dir = PROJECT_ROOT / "dataset_koleroga"
    if koleroga_dir.exists():
        for p in koleroga_dir.rglob("*.*"):
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                candidates.append({
                    "source_type": "file",
                    "repo": "dataset_koleroga",
                    "path": p,
                    "subpath": str(p.relative_to(koleroga_dir)),
                    "name": p.name
                })

    # 2. dataset_patches
    patches_dir = PROJECT_ROOT / "dataset_patches"
    if patches_dir.exists():
        for p in patches_dir.rglob("*.*"):
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                candidates.append({
                    "source_type": "file",
                    "repo": "dataset_patches",
                    "path": p,
                    "subpath": str(p.relative_to(patches_dir)),
                    "name": p.name
                })

    # 3. dataset_raw.zip
    raw_zip = Path(r"C:\Users\Hrushikesh Mirji\Desktop\New folder\zip files\dataset_raw.zip")
    if raw_zip.exists():
        try:
            with zipfile.ZipFile(raw_zip, "r") as z:
                for info in z.infolist():
                    ext = Path(info.filename).suffix.lower()
                    if info.is_dir() or ext not in {".jpg", ".jpeg", ".png"}:
                        continue
                    if "syn_" in info.filename or "synthetic" in info.filename.lower():
                        continue
                    candidates.append({
                        "source_type": "zip",
                        "repo": "dataset_raw.zip",
                        "zip_path": raw_zip,
                        "subpath": info.filename,
                        "name": Path(info.filename).name
                    })
        except Exception as e:
            print(f"    Warning: Error reading dataset_raw.zip: {e}")

    # 4. dataset0000.zip (betel_nut_images subset)
    zip0000 = Path(r"C:\Users\Hrushikesh Mirji\Downloads\dataset0000.zip")
    if zip0000.exists():
        try:
            with zipfile.ZipFile(zip0000, "r") as z:
                for info in z.infolist():
                    ext = Path(info.filename).suffix.lower()
                    if info.is_dir() or ext not in {".jpg", ".jpeg", ".png"}:
                        continue
                    # Only take betel_nut_images photographic folder
                    if "betel_nut_images" in info.filename:
                        candidates.append({
                            "source_type": "zip",
                            "repo": "dataset0000.zip",
                            "zip_path": zip0000,
                            "subpath": info.filename,
                            "name": Path(info.filename).name
                        })
        except Exception as e:
            print(f"    Warning: Error reading dataset0000.zip: {e}")

    print(f"    Found {len(candidates)} total candidate raw files across all legacy sources.")
    return candidates


def read_candidate_bytes(cand: Dict) -> bytes:
    if cand["source_type"] == "file":
        with open(cand["path"], "rb") as f:
            return f.read()
    elif cand["source_type"] == "zip":
        with zipfile.ZipFile(cand["zip_path"], "r") as z:
            return z.read(cand["subpath"])
    raise ValueError("Unknown source type")


def main():
    print("=" * 75)
    print("  ARECAGUARD - LEGACY DATASET SANITIZATION & AI CLASSIFICATION")
    print("=" * 75)

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for c in CANONICAL_CLASSES:
        (OUTPUT_ROOT / c).mkdir(parents=True, exist_ok=True)

    active_hashes = load_active_hashes()
    seen_hashes = set(active_hashes)

    candidates = collect_candidate_sources()

    # Load ViT Model
    print(f"\n[3] Loading fine-tuned ViT classifier from {WEIGHTS_DIR}...")
    processor = ViTImageProcessor.from_pretrained(str(WEIGHTS_DIR))
    model = ViTForImageClassification.from_pretrained(str(WEIGHTS_DIR))
    model.eval()

    device = torch.device("cpu")
    model.to(device)

    rejection_counts = {
        "corrupt": 0,
        "low_resolution": 0,
        "bad_aspect_ratio": 0,
        "low_variance": 0,
        "duplicate_hash": 0,
        "low_confidence": 0,
    }

    class_counts = {c: 0 for c in CANONICAL_CLASSES}
    manifest = []
    rejection_log = []

    print("\n[4] Running 5-Gate Sanitization & Classification Pipeline...")
    t_start = time.time()

    # Pre-filtering with Gates 1-4
    valid_batch_items = []

    for idx, cand in enumerate(candidates):
        if (idx + 1) % 500 == 0 or idx == len(candidates) - 1:
            print(f"    Scanning candidates: {idx+1}/{len(candidates)} ({((idx+1)/len(candidates))*100:.1f}%)...")

        try:
            raw_bytes = read_candidate_bytes(cand)
        except Exception:
            rejection_counts["corrupt"] += 1
            continue

        # Gate 4: Hash deduplication
        h = compute_md5(raw_bytes)
        if h in seen_hashes:
            rejection_counts["duplicate_hash"] += 1
            continue

        # Gate 1: Decodability & Color
        try:
            pil_img = Image.open(io.BytesIO(raw_bytes))
            pil_img.verify()
            # Reopen because verify() closes image
            pil_img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        except Exception:
            rejection_counts["corrupt"] += 1
            continue

        w, h_dim = pil_img.size

        # Gate 2: Resolution & Aspect Ratio
        if w < MIN_DIM or h_dim < MIN_DIM:
            rejection_counts["low_resolution"] += 1
            continue

        aspect = w / float(h_dim)
        if aspect < 0.25 or aspect > 4.0:
            rejection_counts["bad_aspect_ratio"] += 1
            continue

        # Gate 3: Texture & Information Density
        var = check_variance(pil_img)
        if var < MIN_VARIANCE:
            rejection_counts["low_variance"] += 1
            continue

        # Passes Gates 1-4!
        seen_hashes.add(h)
        valid_batch_items.append({
            "cand": cand,
            "img": pil_img,
            "orig_size": (w, h_dim),
            "variance": round(var, 2),
            "md5": h
        })

        # Process in batches when batch size is reached
        if len(valid_batch_items) >= BATCH_SIZE:
            _process_batch(
                valid_batch_items,
                model,
                processor,
                device,
                class_counts,
                rejection_counts,
                manifest,
                rejection_log
            )
            valid_batch_items = []

    # Final remaining batch
    if valid_batch_items:
        _process_batch(
            valid_batch_items,
            model,
            processor,
            device,
            class_counts,
            rejection_counts,
            manifest,
            rejection_log
        )
        valid_batch_items = []

    t_elapsed = time.time() - t_start

    # Save manifest and rejection log
    manifest_path = OUTPUT_ROOT / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    report_path = OUTPUT_ROOT / "sanitization_report.json"
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_scanned": len(candidates),
        "total_accepted": len(manifest),
        "total_rejected": sum(rejection_counts.values()),
        "time_elapsed_sec": round(t_elapsed, 2),
        "rejection_breakdown": rejection_counts,
        "class_distribution": class_counts,
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 75)
    print("  LEGACY DATASET SANITIZATION COMPLETE")
    print("=" * 75)
    print(f"Total Candidates Scanned : {len(candidates)}")
    print(f"Total Images Accepted    : {len(manifest)} ({len(manifest)/len(candidates)*100:.1f}%)")
    print(f"Total Rejected           : {sum(rejection_counts.values())}")
    print(f"Processing Time          : {t_elapsed:.1f} seconds ({t_elapsed/60:.2f} mins)")
    print("\nRejection Breakdown:")
    for reason, count in rejection_counts.items():
        print(f"  - {reason:<22}: {count}")
    print("\nAccepted Clean Class Distribution:")
    for cls_name, count in sorted(class_counts.items()):
        print(f"  - {cls_name:<22}: {count}")
    print(f"\nManifest saved to        : {manifest_path}")
    print(f"Report saved to          : {report_path}")
    print("=" * 75)


def _process_batch(
    items: List[Dict],
    model: ViTForImageClassification,
    processor: ViTImageProcessor,
    device: torch.device,
    class_counts: Dict[str, int],
    rejection_counts: Dict[str, int],
    manifest: List[Dict],
    rejection_log: List[Dict]
):
    images = [it["img"] for it in items]
    inputs = processor(images=images, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        confs, preds = probs.max(dim=-1)

    for i, it in enumerate(items):
        conf = float(confs[i].item())
        pred_idx = int(preds[i].item())
        pred_label = model.config.id2label[pred_idx]
        cand = it["cand"]
        orig_img = it["img"]
        orig_size = it["orig_size"]
        md5_val = it["md5"]

        # Gate 5: AI Confidence Cutoff
        if conf < CONFIDENCE_THRESHOLD:
            rejection_counts["low_confidence"] += 1
            rejection_log.append({
                "subpath": cand.get("subpath", str(cand.get("path", ""))),
                "reason": "low_confidence",
                "pred_label": pred_label,
                "confidence": round(conf, 4)
            })
            continue

        # Accepted! Normalize resolution if > 1024
        normalized_img = normalize_image(orig_img)
        final_w, final_h = normalized_img.size

        # Increment class count and format systematic filename
        class_counts[pred_label] += 1
        seq_num = class_counts[pred_label]
        target_filename = f"{pred_label}_leg_{seq_num:04d}.jpg"
        target_path = OUTPUT_ROOT / pred_label / target_filename

        # Save clean JPEG
        normalized_img.save(target_path, "JPEG", quality=95, optimize=True)

        manifest.append({
            "filename": target_filename,
            "class": pred_label,
            "confidence": round(conf, 4),
            "original_repo": cand.get("repo", "unknown"),
            "original_path": cand.get("subpath", str(cand.get("path", ""))),
            "original_size": orig_size,
            "final_size": (final_w, final_h),
            "variance": it["variance"],
            "md5": md5_val
        })


if __name__ == "__main__":
    main()
