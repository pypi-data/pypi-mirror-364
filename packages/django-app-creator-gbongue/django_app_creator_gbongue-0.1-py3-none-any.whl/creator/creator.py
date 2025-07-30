import os
import shutil
import sys

def create_app(app_name, target_dir="."):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, "templates", "__app_name__")

    app_dir = os.path.join(target_dir, app_name)
    if os.path.exists(app_dir):
        print(f"L'app {app_name} existe déjà.")
        return

    shutil.copytree(template_dir, app_dir)

    for dirpath, _, filenames in os.walk(app_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            with open(filepath, 'r') as f:
                content = f.read()
            content = content.replace("__app_name__", app_name)
            with open(filepath, 'w') as f:
                f.write(content)

    print(f"✅ App Django '{app_name}' créée avec succès !")


    def create_cli():
    if len(sys.argv) < 2:
        print("Usage : django-createapp <nom_de_l_app>")
        return
    app_name = sys.argv[1]
    create_app(app_name)
