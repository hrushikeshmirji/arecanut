import zipfile
import io
from pathlib import Path
from PIL import Image

raw_zip = Path(r"C:\Users\Hrushikesh Mirji\Desktop\New folder\zip files\dataset_raw.zip")
if raw_zip.exists():
    with zipfile.ZipFile(raw_zip, 'r') as z:
        class_stats = {}
        for info in z.infolist():
            ext = Path(info.filename).suffix.lower()
            if info.is_dir() or ext not in ['.jpg', '.jpeg', '.png']:
                continue
            parts = info.filename.split('/')
            cls = parts[1] if len(parts) > 1 else 'root'
            if cls not in class_stats:
                class_stats[cls] = {'count': 0, 'sample_sizes': [], 'synthetic_names': 0}
            class_stats[cls]['count'] += 1
            if 'syn_' in info.filename or 'synthetic' in info.filename.lower():
                class_stats[cls]['synthetic_names'] += 1
            if len(class_stats[cls]['sample_sizes']) < 4:
                try:
                    data = z.read(info.filename)
                    im = Image.open(io.BytesIO(data))
                    class_stats[cls]['sample_sizes'].append(im.size)
                except Exception:
                    pass
        print("=== dataset_raw.zip Summary ===")
        for k, v in sorted(class_stats.items()):
            print(f"  Class: {k:<45} Count: {v['count']:<6} Syn: {v['synthetic_names']:<4} Samples: {v['sample_sizes']}")

zip0000 = Path(r"C:\Users\Hrushikesh Mirji\Downloads\dataset0000.zip")
if zip0000.exists():
    with zipfile.ZipFile(zip0000, 'r') as z:
        classes = {}
        for info in z.infolist():
            ext = Path(info.filename).suffix.lower()
            if info.is_dir() or ext not in ['.jpg', '.jpeg', '.png']:
                continue
            parts = info.filename.split('/')
            folder = '/'.join(parts[:2]) if len(parts) > 2 else parts[0]
            classes[folder] = classes.get(folder, 0) + 1
        print("\n=== dataset0000.zip Summary ===")
        for k, v in sorted(classes.items())[:20]:
            print(f"  Folder: {k:<45} Count: {v}")
