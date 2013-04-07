from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Originally found at http://stackoverflow.com/a/8000091/564584, thanks!"""
    return dictionary.get(key)
