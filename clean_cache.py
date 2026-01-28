import shutil
from pathlib import Path

from tqdm import tqdm

root = Path.cwd()
cache_dirs = sorted(root.rglob("__pycache__"))

print(f"{len(cache_dirs)=}")

for d, dir_path in enumerate(tqdm(cache_dirs, desc="Removing __pycache__")):
    try:
        shutil.rmtree(dir_path)
    except Exception as e:
        print(f"Failed to remove {dir_path}: {e}")
