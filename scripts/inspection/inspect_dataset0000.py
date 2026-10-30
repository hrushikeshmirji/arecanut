import zipfile
from pathlib import Path

zip0000 = Path(r"C:\Users\Hrushikesh Mirji\Downloads\dataset0000.zip")
if zip0000.exists():
    with zipfile.ZipFile(zip0000, 'r') as z:
        folders = {}
        for name in z.namelist():
            parts = name.split('/')
            if len(parts) >= 3 and parts[0] == 'dataset' and parts[1] == 'dataset':
                sub = parts[2]
                folders[sub] = folders.get(sub, 0) + 1
            elif len(parts) >= 3 and parts[0] == 'dataset' and parts[1] == 'betel_nut_images':
                sub = parts[2]
                folders['betel/' + sub] = folders.get('betel/' + sub, 0) + 1
        print("=== dataset0000 subfolders ===")
        for k, v in sorted(folders.items()):
            print(f"  {k}: {v}")
