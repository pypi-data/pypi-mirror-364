from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('cv/<int:id>/', views.lookup, name='lookup'),
]