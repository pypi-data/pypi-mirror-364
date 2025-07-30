import os
import sys
import re

def to_snake_case(name):
    """Transforme 'Mon App' ou 'mon-app' en 'mon_app'"""
    return re.sub(r'[^a-zA-Z0-9]', '_', name.strip()).lower()

def to_camel_case(name):
    """Transforme 'mon_app' ou 'mon-app' en 'MonApp'"""
    parts = re.split(r'[^a-zA-Z0-9]', name.strip())
    return ''.join(word.capitalize() for word in parts if word)

def create_app_structure(app_name_original):
    app_name = to_snake_case(app_name_original)
    class_name = to_camel_case(app_name)

    dirs = [
        f"{app_name}/migrations",
        f"{app_name}/models",
        f"{app_name}/views",
        f"{app_name}/templates/{app_name}",
        f"{app_name}/static/{app_name}",
    ]

    files = {
        f"{app_name}/migrations/__init__.py": "",
        f"{app_name}/models/__init__.py": "",
        f"{app_name}/views/__init__.py": "",
        f"{app_name}/templates/{app_name}/my_template.html": "<!-- Template HTML -->",
        f"{app_name}/static/{app_name}/style.css": "/* CSS */",
        f"{app_name}/__init__.py": "",
        f"{app_name}/urls.py": """from django.urls import path

urlpatterns = [
    # path('', views.index, name='index'),
]
""",
        f"{app_name}/apps.py": f"""from django.apps import AppConfig

class {class_name}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
""",
        f"{app_name}/admin.py": "from django.contrib import admin\n",
        f"{app_name}/tests.py": "# tests",
    }

    for directory in dirs:
        os.makedirs(directory, exist_ok=True)

    for path, content in files.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    print(f"Application '{app_name}' créée avec succès.")

if __name__ == "__main__":
    full_app_name = " ".join(sys.argv[1:]).strip()
    if not full_app_name:
        print("Veuillez entrer un nom pour l'application.")
        sys.exit(1)
    create_app_structure(full_app_name)

