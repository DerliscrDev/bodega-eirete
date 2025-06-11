from django import template

register = template.Library()

@register.filter
def tiene_permiso(user, nombre_permiso):
    if user.is_authenticated and hasattr(user, 'rol') and user.rol:
        return user.rol.permisos.filter(nombre=nombre_permiso, activo=True).exists()
    return False

@register.filter
def filter_by_iva(detalles, iva):
    return [d for d in detalles if d.iva_aplicado == iva]

@register.filter
def subtotal_iva(detalles):
    return sum(d.subtotal() for d in detalles)