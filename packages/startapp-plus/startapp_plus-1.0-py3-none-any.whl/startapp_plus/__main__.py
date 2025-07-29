# startapp_plus/__main__.py

import sys
from .generator import create_app

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Nom de l'application requis ! Exemple : python -m startapp_plus myapp")
    else:
        app_name = sys.argv[1]
        create_app(app_name)

def main():
    print("Bienvenue dans startapp-plus ! 🎉")

if __name__ == "__main__":
    main()