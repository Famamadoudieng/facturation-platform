# evenements/urls.py
from django.urls import path
from . import views

app_name = 'evenements'

urlpatterns = [
    path('', views.EvenementListView.as_view(), name='liste'),
    path('<int:pk>/', views.EvenementDetailView.as_view(), name='detail'),
    path('ajouter/', views.EvenementCreateView.as_view(), name='ajouter'),
    path('<int:pk>/modifier/', views.EvenementUpdateView.as_view(), name='modifier'),
    path('<int:pk>/supprimer/', views.EvenementDeleteView.as_view(), name='supprimer'),
    
    ]