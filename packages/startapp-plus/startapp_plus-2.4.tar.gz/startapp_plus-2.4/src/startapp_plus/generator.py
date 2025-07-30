import shutil
from pathlib import Path
import re

def to_snake_case(name: str) -> str:
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_NAME = "mon_app"
TEMPLATE_APP_DIR = BASE_DIR / TEMPLATE_NAME

def create_app(raw_name: str):
    app_name = to_snake_case(raw_name)
    target_dir = Path.cwd() / app_name

    if target_dir.exists():
        print(f"⚠️ L'application '{app_name}' existe déjà.")
        return

    # Étape 1 : copier toute la structure template
    shutil.copytree(TEMPLATE_APP_DIR, target_dir)

    # Étape 2 : remplacement du contenu dans tous les fichiers
    for file in target_dir.rglob("*"):
        if file.is_file():
            try:
                content = file.read_text(encoding='utf-8')
                new_content = content.replace(TEMPLATE_NAME, app_name)
                file.write_text(new_content, encoding='utf-8')
            except Exception as e:
                print(f"Erreur traitement fichier {file}: {e}")

    # Étape 3 : renommer tous les dossiers qui s'appellent 'mon_app'
    for folder in sorted(target_dir.rglob("*"), reverse=True):
        if folder.is_dir() and folder.name == TEMPLATE_NAME:
            new_folder = folder.parent / app_name
            folder.rename(new_folder)

    print(f"✅ Application Django '{app_name}' générée avec succès !")
