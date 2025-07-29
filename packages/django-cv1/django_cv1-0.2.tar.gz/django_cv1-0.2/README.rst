=============
django-cv1

django-cv1 est une application Django pour réaliser un cv en ligne. Pour chaque question.Vous pouvez utiliser le formulaire et l'adapter a votre cv

La documentation détaillée se trouve dans le répertoire "docs".
Démarrage rapide

    Ajoutez "cv" à votre paramètre INSTALLED_APPS comme ceci :

    INSTALLED_APPS = [
    ...,
    "django_cv1",
    ]

    Incluez l'URLconf de cv dans votre fichier urls.py de projet comme ceci :

    path("cv/", include("django_cv1.urls")),

    Exécutez python manage.py migrate pour créer les modèles.

    Démarrez le serveur de développement.



