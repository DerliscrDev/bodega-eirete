from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def tiene_permiso(context, nombre_permiso):
    user = context['request'].user
    if user.is_authenticated and hasattr(user, 'rol') and user.rol:
        return user.rol.permisos.filter(nombre=nombre_permiso, activo=True).exists()
    return False