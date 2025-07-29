# startapp_plus/__main__.py

import sys
from .generator import create_app

def main():
    if len(sys.argv) < 2:
        print("Nom de l'application requis ! Exemple : startapp-plus nom_de_mon_app")
    else:
        app_name = sys.argv[1]
        create_app(app_name)
