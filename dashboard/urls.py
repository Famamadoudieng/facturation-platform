
from django.urls import path
from . import views

app_name = 'dashboard'  # ← Important pour le namespace

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # ← Le name='dashboard' est ici
]
