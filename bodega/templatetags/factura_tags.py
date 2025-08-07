# bodega/templatetags/factura_tags.py
from django import template

register = template.Library()

@register.filter
def filter_by_iva(detalles, iva):
    return [d for d in detalles if d.iva_aplicado == iva]

@register.filter
def sum_subtotal(detalles):
    return sum([d.subtotal() for d in detalles])
