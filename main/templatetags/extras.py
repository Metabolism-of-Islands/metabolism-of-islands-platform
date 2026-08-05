from django import template
from django.template.defaulttags import register

register = template.Library()

@register.filter
def get_item(dictionary, key):
    try:
        if dictionary.get(key) is not None:
            return dictionary.get(key)
        elif dictionary.get(str(key)) is not None:
            return dictionary.get(str(key))
        else:
            return ""
    except:
        return ""

# For OPTamos
@register.filter
def concat(value1, value2):
    return f"{value1}{value2}"

# Also for OPTamos
@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

