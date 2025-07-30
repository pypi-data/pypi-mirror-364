import os
import sys

def slugify(name):
    return name.replace("-", "_").replace(" ", "_").lower()

def camelize(name):
    return ''.join(word.capitalize() for word in name.replace("-", " ").replace("_", " ").split())

def create_file(path, content=""):
    with open(path, "w") as f:
        f.write(content)
    print(f"Fichier créé : {path}")

def create_directory(path):
    os.makedirs(path, exist_ok=True)
    print(f" Dossier créé : {path}")

def generate_app(app_input_name):
    slug_name = slugify(app_input_name)       # nom dossier/module Django valide
    class_name = camelize(app_input_name)     # nom classe AppConfig

    base_path = os.path.join(".", slug_name)
    create_directory(base_path)

    # Fichiers de base
    create_file(os.path.join(base_path, "__init__.py"))
    create_file(os.path.join(base_path, "admin.py"))
    create_file(os.path.join(base_path, "apps.py"), f"""
from django.apps import AppConfig

class {class_name}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{slug_name}'
""".strip())

    create_file(os.path.join(base_path, "tests.py"))

    # Dossier migrations
    migrations_path = os.path.join(base_path, "migrations")
    create_directory(migrations_path)
    create_file(os.path.join(migrations_path, "__init__.py"))

    # Dossier models
    models_path = os.path.join(base_path, "models")
    create_directory(models_path)
    create_file(os.path.join(models_path, "__init__.py"))
    create_file(os.path.join(models_path, "models.py"))

    # Dossier views
    views_path = os.path.join(base_path, "views")
    create_directory(views_path)
    create_file(os.path.join(views_path, "__init__.py"))
    create_file(os.path.join(views_path, "views.py"))

    # Dossier urls
    urls_path = os.path.join(base_path, "urls")
    create_directory(urls_path)
    create_file(os.path.join(urls_path, "__init__.py"))
    create_file(os.path.join(urls_path, "urls.py"))

    # Dossier templates/slug_name/index.html
    templates_path = os.path.join(base_path, "templates", slug_name)
    create_directory(templates_path)
    create_file(os.path.join(templates_path, "index.html"), f"<h1>Bienvenue sur {slug_name}</h1>")

    # Dossier static/slug_name/style.css
    static_path = os.path.join(base_path, "static", slug_name)
    create_directory(static_path)
    create_file(os.path.join(static_path, "style.css"), f"/* CSS de l'application {slug_name} */")

    print(f"\n✅ Application Django '{slug_name}' générée avec succès !")

# --------- POINT D’ENTRÉE DU SCRIPT ---------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python -m djangoappgen.generator <nom-de-l-app>")
        sys.exit(1)

    # On accepte plusieurs mots comme nom d'app
    app_input_name = " ".join(sys.argv[1:])
    generate_app(app_input_name)
