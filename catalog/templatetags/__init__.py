from django import template

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    """Return dictionary[key], defaulting to 0 if missing. Useful in templates."""
    return dictionary.get(key, 0)
