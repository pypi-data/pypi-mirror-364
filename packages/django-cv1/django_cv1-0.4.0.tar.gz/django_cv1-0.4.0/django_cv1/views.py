from django.shortcuts import render
from .models import Personne
from django.shortcuts import render, redirect
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

        # Rediriger vers la page de résultat avec l'id
        return redirect('lookup', id=personne.id)

    return render(request, "django_cv1/moncv.html")


def lookup(request, id):
    personne = Personne.objects.get(id=id)
    return render(request, "django_cv1/lookup1.html", {"cv": personne})
