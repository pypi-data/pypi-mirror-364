import os
from pathlib import Path
import sys

def snake_to_camel(name):
    return ''.join(word.capitalize() for word in name.split('_'))

def create_app_structure(app_name):
    base = Path(app_name)
    camel_name = snake_to_camel(app_name)

    folders = [
        base / 'migrations',
        base / 'models',
        base / 'views',
        base / 'templates' / app_name,
        base / 'static' / app_name
    ]

    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
        if '__init__.py' not in folder.name:
            (folder / '__init__.py').touch()

    files = {
        base / '__init__.py': '',
        base / 'urls.py': 'from django.urls import path\n\nurlpatterns = []\n',
        base / 'apps.py': f"""from django.apps import AppConfig\n\nclass {camel_name}Config(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = '{app_name}'\n""",
        base / 'admin.py': '',
        base / 'tests.py': '',
        base / 'templates' / app_name / 'my_template.html': '<!-- HTML template -->\n',
        base / 'static' / app_name / 'style.css': '/* CSS */\n'
    }

    for path, content in files.items():
        with open(path, 'w') as f:
            f.write(content)

    print(f"✅ App structure for '{app_name}' created!")

def main():
    if len(sys.argv) < 2:
        print("Usage: djappgen <app_name>")
    else:
        create_app_structure(sys.argv[1])
