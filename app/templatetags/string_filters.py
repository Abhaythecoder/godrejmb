from django import template
register = template.Library()

@register.filter
def replace(value, arg):
    """Replaces all values of arg in the string with ''. Usage: {{ value|replace:" " }}"""
    return value.replace(arg, '')
