# clients/urls.py 
from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.ClientListView.as_view(), name='list'),           # Liste des clients
    path('ajouter/', views.ClientCreateView.as_view(), name='create'), # Ajouter un client
    path('<int:pk>/', views.ClientDetailView.as_view(), name='detail'), # Détail d'un client
    path('<int:pk>/modifier/', views.ClientUpdateView.as_view(), name='update'), # Modifier
    path('<int:pk>/supprimer/', views.ClientDeleteView.as_view(), name='delete'), # Supprimer
]