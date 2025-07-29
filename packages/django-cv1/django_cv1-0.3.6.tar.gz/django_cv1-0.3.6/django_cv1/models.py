from django.db import models

from django.db import models


class Personne(models.Model):
    email = models.EmailField(max_length=200)
    adresse = models.CharField(max_length=200)
    numero = models.CharField(max_length=20)
    profile = models.TextField()
    experience = models.TextField()
    formation = models.TextField()

