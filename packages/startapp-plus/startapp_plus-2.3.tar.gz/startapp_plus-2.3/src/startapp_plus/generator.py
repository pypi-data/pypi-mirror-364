import os
import shutil
from pathlib import Path
import re

def to_snake_case(name: str) -> str:
    # "BlogApp" ou "blogApp" → "blog_app"
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_APP_DIR = BASE_DIR / "mon_app"


def create_app(app_name: str):
    target_dir = Path.cwd() / app_name
    if target_dir.exists():
        print(f"L'app {app_name} existe déjà.")
        return

    shutil.copytree(TEMPLATE_APP_DIR, target_dir)
    print(f"Application Django '{app_name}' générée avec succès !")
