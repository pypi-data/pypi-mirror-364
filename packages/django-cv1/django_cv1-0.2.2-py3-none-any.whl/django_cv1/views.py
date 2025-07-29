from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse

from .models import Personne

def index(request):
        if request.method == 'POST':
            nom_prenom = request.POST.get('nom_prenom')
            email = request.POST.get('email')
            adresse = request.POST.get('adresse')
            numero = request.POST.get('numero')
            profile = request.POST.get('profile')
            formation = request.POST.get('formation')
            experience = request.POST.get('experience')

            # Créer l'objet Personne
            personne = Personne.objects.create(
                nom_prenom=nom_prenom,
                email=email,
                adresse=adresse,
                numero=numero,
                profile=profile,
                formation=formation,
                experience=experience,
            )
        return render(request, "moncv.html",context={'index':index})  # Afficher le formulaire si ce n'est pas un POST

