DoctorCheck

DoctorCheck DoctorCheck est un package Python qui fournit une application Django pour évaluer la santé des utilisateurs en fonction de leur tension artérielle et d'autres symptômes, sans utiliser de base de données. Il inclut une interface interactive HTML/CSS/JS pour collecter les données et fournir un diagnostic simple. Installation pip install doctorcheck

Installation





Installez le package via pip :

pip install doctorcheck



Ajoutez medicaleformulaire à INSTALLED_APPS dans settings.py :

INSTALLED_APPS = [
    ...
    'doctorcheck',
]



Incluez les URLs dans urls.py de votre projet :

from django.urls import include, path

urlpatterns = [ ... path("health/", include("doctorcheck.urls")), ]



Chargez les fichiers statiques dans votre template de base ou exécutez :

python manage.py collectstatic

Utilisation

Accédez à l'URL /health/ pour voir le formulaire d'évaluation. Entrez l'âge, la tension systolique, la tension diastolique, et cochez les symptômes (maux de tête, fatigue). Soumettez le formulaire pour obtenir un diagnostic.



Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.