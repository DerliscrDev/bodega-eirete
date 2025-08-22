# bodega/templatetags/nav_tags.py
from django import template
register = template.Library()

@register.simple_tag(takes_context=True)
def active(context, *url_names):
    """Devuelve 'active' si la URL actual está en url_names."""
    try:
        current = context['request'].resolver_match.url_name
    except Exception:
        return ''
    return 'active' if current in url_names else ''
