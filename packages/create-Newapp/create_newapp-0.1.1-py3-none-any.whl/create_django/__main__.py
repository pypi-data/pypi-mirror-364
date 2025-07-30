import os
import shutil
import sys

def copy_template(app_name):
    src_dir = os.path.join(os.path.dirname(__file__), "Myapp")
    dst_dir = os.path.abspath(app_name)

    if os.path.exists(dst_dir):
        print(f"Erreur : le dossier '{app_name}' existe déjà.")
        sys.exit(1)

    shutil.copytree(src_dir, dst_dir)

    # Remplace APP_NAME dans apps.py
    apps_file = os.path.join(dst_dir, "apps.py")
    with open(apps_file, "r", encoding="utf-8") as f:
        content = f.read().replace("APP_NAME", app_name)

    with open(apps_file, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Application Django '{app_name}' créée avec succès dans {dst_dir}")

def main():
    if len(sys.argv) != 2:
        print("Usage : create-django <nom_de_l_app>")
        sys.exit(1)

    app_name = sys.argv[1]
    copy_template(app_name)

if __name__ == "__main__":
    main()