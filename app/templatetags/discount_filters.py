from django import template
register = template.Library()

@register.filter
def discount_percent(original_price, discounted_price):
    try:
        original = float(original_price)
        discounted = float(discounted_price)
        if original > discounted and original > 0:
            percent = ((original - discounted) / original) * 100
            return int(round(percent))
        return None
    except (ValueError, TypeError):
        return None
