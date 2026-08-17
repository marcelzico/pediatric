# patient/templatetags/exam_tags.py
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def fields_by_prefix(form, prefix):
    return [field for field in form if field.name.startswith(prefix)]