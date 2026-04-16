# clients/admin.py
from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['nom', 'email', 'telephone']
    search_fields = ['nom', 'email']