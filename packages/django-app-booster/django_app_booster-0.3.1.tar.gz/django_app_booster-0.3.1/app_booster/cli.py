import os
import sys
import subprocess
import re

def normalize_app_name(name):
    # Remplacer espaces et tirets par underscore
    name = name.strip().lower()
    name = re.sub(r'[\s\-]+', '_', name)
    # Enlever tout caractère non alphanumérique ou underscore
    name = re.sub(r'[^\w]', '', name)
    return name

def create_boosted_app(raw_name):
    app_name = normalize_app_name(raw_name)
    print(f"Création de l'app Django personnalisée : {app_name}")

    subprocess.run(["django-admin", "startapp", app_name])

    if not os.path.exists(app_name):
        print("L'application n'a pas été créée.")
        sys.exit(1)

    # Supprimer les fichiers de base
    for file in ["views.py", "models.py", "tests.py"]:
        path = os.path.join(app_name, file)
        if os.path.exists(path):
            os.remove(path)

    # Créer les dossiers personnalisés
    for folder in ["views", "models", "tests"]:
        folder_path = os.path.join(app_name, folder)
        os.makedirs(folder_path, exist_ok=True)
        open(os.path.join(folder_path, "__init__.py"), 'w').close()

    # Créer urls.py
    urls_content = """from django.urls import path

urlpatterns = [
    # Ajoutez vos vues ici
]
"""
    with open(os.path.join(app_name, "urls.py"), "w") as f:
        f.write(urls_content)

    # Créer templates/<app_name>/ avec base.html
    templates_path = os.path.join(app_name, "templates", app_name)
    os.makedirs(templates_path, exist_ok=True)
    with open(os.path.join(templates_path, "base.html"), "w") as f:
        f.write(f"{{% comment %}} Template de base de l'app {app_name} {{% endcomment %}}\n")

    # Créer static/<app_name>/ avec style.css
    static_path = os.path.join(app_name, "static", app_name)
    os.makedirs(static_path, exist_ok=True)
    with open(os.path.join(static_path, "style.css"), "w") as f:
        f.write(f"/* Styles de l'app {app_name} */\n")

    print(f"App Django '{app_name}' créée avec templates/ et static/ propres.")

def main():
    if len(sys.argv) != 2:
        print("Utilisation : createapp <nom_app>")
        sys.exit(1)

    raw_name = sys.argv[1]
    create_boosted_app(raw_name)

if __name__ == "__main__":
    main()
