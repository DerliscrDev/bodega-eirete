from functools import wraps
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages

def permiso_requerido(codigo_permiso: str):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            u = request.user
            if not u.is_authenticated:
                return redirect_to_login(request.get_full_path())

            # ⬇️ superuser / staff pasan siempre
            if getattr(u, "is_superuser", False) or getattr(u, "is_staff", False):
                return view_func(request, *args, **kwargs)

            # Bootstrap: si aún no cargaste permisos, no bloquees
            from .models import Permiso
            if not Permiso.objects.exists():
                return view_func(request, *args, **kwargs)

            # Hook opcional del modelo Usuario
            if hasattr(u, "has_custom_permission") and u.has_custom_permission(codigo_permiso):
                return view_func(request, *args, **kwargs)

            messages.warning(request, "No tenés permiso para acceder a esta página.")
            from django.shortcuts import redirect
            return redirect("home")
        return _wrapped
    return decorator


# from django.shortcuts import redirect
# from django.core.exceptions import PermissionDenied

# def permiso_requerido(nombre_permiso):
#     def decorator(view_func):
#         def _wrapped_view(request, *args, **kwargs):
#             if not request.user.is_authenticated:
#                 return redirect('login')

#             # Si es superusuario, acceso total
#             if request.user.is_superuser:
#                 return view_func(request, *args, **kwargs)

#             # Verificamos que tenga rol
#             if not hasattr(request.user, 'rol') or request.user.rol is None:
#                 raise PermissionDenied("El usuario no tiene roles asignados.")

#             if request.user.rol.permisos.filter(nombre=nombre_permiso, activo=True).exists():
#                 return view_func(request, *args, **kwargs)

#             raise PermissionDenied("No tienes permiso para acceder a esta vista.")
#         return _wrapped_view
#     return decorator