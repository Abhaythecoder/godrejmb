from django import template

register = template.Library()

@register.filter
def split(value, key):
    """
    Splits a string by a given key.
    Usage: {{ value|split:"," }}
    """
    return value.split(key)

@register.filter
def get_by_id(products, product_id):
    return products.get(pk=product_id)

@register.filter
def multiply(value, arg):
    return int(value) * int(arg)