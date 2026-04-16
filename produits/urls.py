# produits/urls.py
from django.urls import path
from . import views

app_name = 'produits'

urlpatterns = [
    path('', views.ProduitListView.as_view(), name='list'),
    path('ajouter/', views.ProduitCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ProduitDetailView.as_view(), name='detail'),
    path('<int:pk>/modifier/', views.ProduitUpdateView.as_view(), name='update'),
    path('<int:pk>/supprimer/', views.ProduitDeleteView.as_view(), name='delete'),
]