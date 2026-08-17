# patient/templatetags/exam_tags.py
from django import template

register = template.Library()


@register.filter
def fields_by_prefix(form, prefix):
    """
    Filtre les champs d'un formulaire dont le nom commence par un préfixe donné.
    Utilisation : {% for field in subform|fields_by_prefix:"inspection_" %}
    """
    return [field for field in form if field.name.startswith(prefix)]


@register.filter
def fields_by_prefix(form, prefix):
    """
    Filtre les champs d'un formulaire dont le nom commence par un préfixe donné.
    """
    return [field for field in form if field.name.startswith(prefix)]


@register.filter
def has_fields_with_prefix(form, prefix):
    """
    Vérifie si un formulaire a au moins un champ avec le préfixe donné.
    """
    return any(field.name.startswith(prefix) for field in form)


@register.filter
def get_item(dictionary, key):
    """
    Permet d'accéder à un élément d'un dictionnaire dans un template.
    """
    if dictionary is None:
        return None
    return dictionary.get(key)