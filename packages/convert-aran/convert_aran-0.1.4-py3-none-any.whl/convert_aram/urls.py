# convert_aram/urls.py

from django.urls import path
from . import views

app_name= "convert_aram"

urlpatterns = [
    path('', views.index, name='index'),
    path('resultat/',views.resultat, name='resultat_page'),
]
