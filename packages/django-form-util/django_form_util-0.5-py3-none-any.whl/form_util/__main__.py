import sys
import shutil
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Nom du package requis ! Exemple : form_util nom_app")
        return

    app_name = sys.argv[1]
    current_dir = Path.cwd()
    target_dir = current_dir / app_name

    if target_dir.exists():
        print(f"Le dossier '{app_name}' existe déjà.")
        return

    # Chemin absolu vers le dossier "template" dans le package
    template_dir = Path(__file__).resolve().parent / "templates"

    try:
        shutil.copytree(template_dir, target_dir)
        print(f"Le package Django '{app_name}' a été généré avec succès !")
    except Exception as e:
        print(f"Erreur : {e}")
