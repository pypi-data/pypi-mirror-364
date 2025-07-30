# startapp_plus/__main__.py

import sys
from .generator import create_app, to_snake_case

def main():
    if len(sys.argv) < 2:
        print("Nom de l'application requis ! Exemple : startapp-plus nom_de_mon_app")
    else:
        app_name = sys.argv[1]
        create_app(app_name)

    raw_name = sys.argv[1]
    app_name = to_snake_case(raw_name)
    print(f"🔧 Nom formaté : {app_name}")
    create_app(app_name)

if __name__ == "__main__":
    main()
