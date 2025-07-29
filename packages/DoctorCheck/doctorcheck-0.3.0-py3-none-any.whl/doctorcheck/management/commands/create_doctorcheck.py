from django.core.management.base import BaseCommand
from django.core.management import call_command
import os
import shutil
from pathlib import Path

class Command(BaseCommand):
    help = "Crée l'application DoctorCheck dans le projet Django actuel."

    def handle(self, *args, **options):
        app_name = "doctorcheck"
        project_dir = Path.cwd()
        app_dir = project_dir / app_name

        # Vérifier si l'application existe déjà
        if app_dir.exists():
            self.stdout.write(self.style.ERROR(f"L'application '{app_name}' existe déjà dans ce projet."))
            return

        # Créer l'application avec startapp
        call_command("startapp", app_name)

        # Obtenir le chemin du package installé
        package_dir = Path(__file__).parent.parent.parent

        # Copier les fichiers spécifiques du package vers l'application
        files_to_copy = [
            ("templates", ["base.html", "health_check.html"]),
            ("static/css", ["style.css"]),
            ("static/js", ["script.js"]),
            ("", ["apps.py", "urls.py", "views.py", "health_logic.py"]),
        ]

        for folder, files in files_to_copy:
            src_dir = package_dir / folder
            dest_dir = app_dir / folder
            if folder and not dest_dir.exists():
                dest_dir.mkdir(parents=True)
            for file in files:
                src_file = src_dir / file
                dest_file = dest_dir / file
                if src_file.exists():
                    shutil.copy2(src_file, dest_file)
                    self.stdout.write(self.style.SUCCESS(f"Copié : {dest_file}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Fichier non trouvé : {src_file}"))

        self.stdout.write(self.style.SUCCESS(f"Application '{app_name}' créée avec succès."))
        self.stdout.write(
            "Ajoutez 'doctorcheck' à INSTALLED_APPS dans settings.py et incluez 'doctorcheck.urls' dans urls.py."
        )
