# patient/templatetags/custom_filters.py
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Permet d'accéder à un élément d'un dictionnaire dans un template Django.
    Utilisation : {{ my_dict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
