# DoctorCheck

DoctorCheck est un package Python qui fournit une application Django pour évaluer la santé des utilisateurs en fonction de leur tension artérielle et d'autres symptômes, sans utiliser de base de données. Il inclut une interface interactive HTML/CSS/JS pour collecter les données et fournir un diagnostic simple.

## Installation

```bash
pip install doctorcheck
```

## Création de l'application

Après avoir installé le package, vous pouvez créer l'application Django `doctorcheck` dans votre projet avec la commande suivante :

```bash
python manage.py create_doctorcheck
```

Cela générera automatiquement l'application `doctorcheck` avec tous les fichiers nécessaires (vues, templates, fichiers statiques, etc.).

## Configuration

1. Ajoutez "doctorcheck" à `INSTALLED_APPS` dans votre fichier `settings.py` :

```python
INSTALLED_APPS = [
    ...
    "doctorcheck",
]
```

2. Incluez les URLs dans votre fichier `urls.py` principal :

```python
from django.urls import include, path

urlpatterns = [
    ...
    path("health/", include("doctorcheck.urls")),
]
```

3. Assurez-vous que les fichiers statiques sont collectés :

```bash
python manage.py collectstatic
```

## Utilisation

- Accédez à l'URL `/health/` pour voir le formulaire d'évaluation.
- Entrez l'âge, la tension systolique, la tension diastolique, et cochez les symptômes (maux de tête, fatigue).
- Soumettez le formulaire pour obtenir un diagnostic.



## Licence

MIT
