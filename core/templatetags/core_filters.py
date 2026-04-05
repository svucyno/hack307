from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key in templates."""
    return dictionary.get(key, [])

@register.filter
def multiply(value, arg):
    return int(value) * int(arg)
