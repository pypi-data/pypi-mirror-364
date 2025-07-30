import sys
from .main import create_app_structure

if __name__ == "__main__":
    full_app_name = " ".join(sys.argv[1:]).strip()
    if not full_app_name:
        print("Veuillez entrer un nom pour l'application.")
        sys.exit(1)
    create_app_structure(full_app_name)
