# parametres/templatetags/parametres_extras.py
from django import template
from parametres.models import ParametresEntreprise

register = template.Library()

@register.simple_tag
def get_entreprise_logo():
    """Récupère le logo de l'entreprise"""
    try:
        entreprise = ParametresEntreprise.get_instance()
        return entreprise.logo
    except:
        return None

@register.simple_tag
def get_entreprise_nom():
    """Récupère le nom de l'entreprise"""
    try:
        entreprise = ParametresEntreprise.get_instance()
        return entreprise.nom_entreprise
    except:
        return "Facturation Pro"# parametres/templatetags/parametres_extras.py
from django import template
from parametres.models import ParametresEntreprise

register = template.Library()

@register.simple_tag
def get_entreprise_logo():
    """Récupère le logo de l'entreprise"""
    try:
        entreprise = ParametresEntreprise.get_instance()
        return entreprise.logo
    except:
        return None

@register.simple_tag
def get_entreprise_nom():
    """Récupère le nom de l'entreprise"""
    try:
        entreprise = ParametresEntreprise.get_instance()
        return entreprise.nom_entreprise
    except:
        return "Facturation Pro"