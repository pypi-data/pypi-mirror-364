import os
import sys
import re

def to_camel_case(name):
    # Remplacer les espaces ou tirets par des underscores
    normalized_name = re.sub(r'[- ]+', '_', name.strip())
    # Diviser par underscore et capitaliser chaque mot
    words = normalized_name.split('_')
    # Joindre les mots en CamelCase
    return ''.join(word.capitalize() for word in words if word)

def to_snake_case(name):
    # Remplacer les espaces ou tirets par des underscores
    normalized_name = re.sub(r'[- ]+', '_', name.strip())
    # Convertir en minuscules et joindre avec des underscores
    words = [word.lower() for word in normalized_name.split('_') if word]
    return '_'.join(words)

def validate_app_name(app_name):
    # Vérifier si le nom est valide (lettres, chiffres, tirets, underscores, espaces)
    if not re.match(r'^[a-zA-Z0-9_\-\s]+$', app_name):
        raise ValueError("Le nom de l'application ne doit contenir que des lettres, chiffres, tirets, underscores ou espaces.")
    # Convertir en snake_case
    return to_snake_case(app_name)

def custom_app(app_name):
    try:
        # Valider et convertir le nom de l'application en snake_case
        app_name = validate_app_name(app_name)
        # Créer les répertoires
        os.makedirs(app_name, exist_ok=True)
        os.makedirs(f"{app_name}/models", exist_ok=True)
        os.makedirs(f"{app_name}/views", exist_ok=True)
        os.makedirs(f"{app_name}/migrations", exist_ok=True)

        # Fichiers de base
        with open(f"{app_name}/migrations/__init__.py", "w"): pass
        with open(f"{app_name}/__init__.py", "w"): pass

        with open(f"{app_name}/models/__init__.py", "w") as f:
            f.write("# models here\n")

        with open(f"{app_name}/views/__init__.py", "w") as f:
            f.write("# views here\n")

        with open(f"{app_name}/urls.py", "w") as f:
            f.write(
                "from django.urls import path\n\n"
                "urlpatterns = [\n"
                "    # path('', views.index, name='index'),\n"
                "]\n"
            )

        with open(f"{app_name}/admin.py", "w") as f:
            f.write("from django.contrib import admin\n\n# Register your models here.\n")

        # Générer le nom de la classe en CamelCase
        class_name = to_camel_case(app_name) + "Config"
        with open(f"{app_name}/apps.py", "w") as f:
            f.write(
                "from django.apps import AppConfig\n\n"
                f"class {class_name}(AppConfig):\n"
                f"    default_auto_field = 'django.db.models.BigAutoField'\n"
                f"    name = '{app_name}'\n"
            )

        with open(f"{app_name}/tests.py", "w") as f:
            f.write(
                "from django.test import TestCase\n\n"
                "# Create your tests here.\n"
            )

        print(f"App Django '{app_name}' créée avec succès !")
    
    except ValueError as e:
        print(f"Erreur : {e}")
    except OSError as e:
        print(f"Erreur lors de la création des fichiers/répertoires : {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage : create-app <nom_app>")
        sys.exit(1)
    else:
        custom_app(sys.argv[1])

if __name__ == "__main__":
    main()