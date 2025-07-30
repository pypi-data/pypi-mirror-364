from django.db import models

from django.db import models


class Personne(models.Model):
    nom_prenom = models.CharField(max_length=200 , blank=True, null=True)
    email = models.EmailField(max_length=200 ,blank=True, null=True)
    adresse = models.CharField(max_length=200, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    profile = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    formation = models.TextField(blank=True, null=True)

