melodie-app-django-creator-two

melodie-app-django-creator-two est un outil en ligne de commande qui génère automatiquement la structure complète d’une application Django. Il crée un dossier avec tous les fichiers indispensables : __init__.py, admin.py, models.py, views.py, urls.py et apps.py. Tu peux ainsi démarrer ton app rapidement, sans perdre de temps.


INSTALLATION

Pour installer le package, ouvre ton terminal et tape :

pip install melodie-app-django-creator-smart


UTILISATION

Avant d’utiliser la commande, assure-toi que Python 3 est bien installé sur ta machine. Il est recommandé de créer et d’activer un environnement virtuel avec python3 -m venv venv et  source venv/bin/activate

Django doit être installé si tu souhaites utiliser l’application générée.

Pour créer une nouvelle application Django, utilise la commande suivante dans ton terminal :

melodie-app-django-creator-two create nomdevotreapp

Tu peux aussi utiliser la version raccourcie sans le mot "create" :

melodie-app-django-creator-smart nomdevotreapp

Un dossier portant le nom de votre application apparaîtra.

