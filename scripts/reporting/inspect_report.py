import json
from pathlib import Path
from collections import Counter

report_path = Path("dataset_legacy_sanitized/sanitization_report.json")
with open(report_path, "r", encoding="utf-8") as f:
    report = json.load(f)

print("Report summary:")
for k, v in report.items():
    if k != "rejection_breakdown" and k != "class_distribution":
        print(f"  {k}: {v}")

print("\nRejection breakdown:")
for k, v in report["rejection_breakdown"].items():
    print(f"  {k}: {v}")

print("\nClass distribution:")
for k, v in report["class_distribution"].items():
    print(f"  {k}: {v}")
