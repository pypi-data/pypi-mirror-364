import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_APP_DIR = BASE_DIR / "templates" / "base_app"

def create_app(app_name: str):
    target_dir = Path.cwd() / app_name
    if target_dir.exists():
        print(f"L'app {app_name} existe déjà.")
        return

    shutil.copytree(TEMPLATE_APP_DIR, target_dir)
    print(f"Application Django '{app_name}' générée avec succès !")
