import os
import sys

def normalize_app_name(app_name):
    """Transforme les tirets en underscore et met en minuscule"""
    return app_name.lower().replace("-", "_")

def to_camel_case(snake_str):
    parts = snake_str.replace(".", "_").replace("-", "_").split("_")
    return ''.join(part.capitalize() for part in parts)

def create_app(app_name):
    normalized_name = normalize_app_name(app_name)
    camel_case_name = to_camel_case(normalized_name)

    # Créer les dossiers principaux
    os.makedirs(normalized_name, exist_ok=True)
    os.makedirs(f"{normalized_name}/models", exist_ok=True)
    os.makedirs(f"{normalized_name}/views", exist_ok=True)
    os.makedirs(f"{normalized_name}/migrations", exist_ok=True)
    os.makedirs(f"templates/{normalized_name}", exist_ok=True)
    os.makedirs(f"static/{normalized_name}", exist_ok=True)

    # Fichiers de base
    open(f"{normalized_name}/__init__.py", "w").close()
    open(f"{normalized_name}/migrations/__init__.py", "w").close()

    with open(f"{normalized_name}/models/__init__.py", "w") as f:
        f.write("# models here\n")

    with open(f"{normalized_name}/views/__init__.py", "w") as f:
        f.write("# views here\n")

    with open(f"{normalized_name}/urls.py", "w") as f:
        f.write(
            "from django.urls import path\n\n"
            "urlpatterns = [\n"
            "    # path('', views.index, name='index'),\n"
            "]\n"
        )

    with open(f"{normalized_name}/admin.py", "w") as f:
        f.write("from django.contrib import admin\n\n# Register your models here.\n")

    with open(f"{normalized_name}/apps.py", "w") as f:
        f.write(
            "from django.apps import AppConfig\n\n"
            f"class {camel_case_name}Config(AppConfig):\n"
            f"    default_auto_field = 'django.db.models.BigAutoField'\n"
            f"    name = '{normalized_name}'\n"
        )

    with open(f"{normalized_name}/tests.py", "w") as f:
        f.write(
            "from django.test import TestCase\n\n"
            "# Create your tests here.\n"
        )

    with open(f"templates/{normalized_name}/base.html", "w") as f:
        f.write(
            "<!DOCTYPE html>\n"
            "<html lang=\"en\">\n"
            "<head>\n"
            "    <meta charset=\"UTF-8\">\n"
            f"    <title>{normalized_name.capitalize()} Template</title>\n"
            f"    <link rel=\"stylesheet\" href=\"{{% static '{normalized_name}/style.css' %}}\">\n"
            "</head>\n"
            "<body>\n"
            "    <h1>Bienvenue dans l'app {{ app_name }}</h1>\n"
            "</body>\n"
            "</html>\n"
        )

    with open(f"static/{normalized_name}/style.css", "w") as f:
        f.write(
            "body {\n"
            "    font-family: Arial, sans-serif;\n"
            "    background-color: #f9f9f9;\n"
            "    margin: 2rem;\n"
            "}\n"
        )

    print(f" App Django '{normalized_name}' créée avec succès !")

def main():
    if len(sys.argv) < 2:
        print("Usage : django-create-app <nom_app>")
    else:
        create_app(sys.argv[1])

if __name__ == "__main__":
    main()
