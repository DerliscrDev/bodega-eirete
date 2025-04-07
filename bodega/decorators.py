# bodega/decorators.py
# from django.shortcuts import redirect
# from django.core.exceptions import PermissionDenied

# def permiso_requerido(nombre_permiso):
#     def decorator(view_func):
#         def _wrapped_view(request, *args, **kwargs):
#             if not request.user.is_authenticated:
#                 return redirect('login')
#             if not hasattr(request.user, 'roles'):
#                 raise PermissionDenied("El usuario no tiene roles asignados.")
#             for rol in request.user.roles.all():
#                 if rol.permisos.filter(nombre=nombre_permiso, activo=True).exists():
#                     return view_func(request, *args, **kwargs)
#             raise PermissionDenied("No tienes permiso para acceder a esta vista.")
#         return _wrapped_view
#     return decorator

from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def permiso_requerido(nombre_permiso):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            # Si es superusuario, acceso total
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Verificamos que tenga rol
            if not hasattr(request.user, 'rol') or request.user.rol is None:
                raise PermissionDenied("El usuario no tiene roles asignados.")

            if request.user.rol.permisos.filter(nombre=nombre_permiso, activo=True).exists():
                return view_func(request, *args, **kwargs)

            raise PermissionDenied("No tienes permiso para acceder a esta vista.")
        return _wrapped_view
    return decorator
