# your_app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='to_str')
def to_str(value):
    return str(value)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)