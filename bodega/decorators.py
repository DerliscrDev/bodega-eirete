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