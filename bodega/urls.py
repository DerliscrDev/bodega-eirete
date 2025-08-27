# bodega/urls.py
from django.urls import path
from .views import (
    HomeView,
    PersonaListView, PersonaCreateView, PersonaUpdateView, persona_inactivate,
    PermisoListView, PermisoCreateView, PermisoUpdateView, permiso_inactivate,
    RolListView, RolCreateView, RolUpdateView, rol_inactivate
)

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),

    # Personas
    path("personas/", PersonaListView.as_view(), name="persona_list"),
    path("personas/nueva/", PersonaCreateView.as_view(), name="persona_create"),
    path("personas/<int:pk>/editar/", PersonaUpdateView.as_view(), name="persona_update"),
    path("personas/<int:pk>/toggle/", persona_inactivate, name="persona_inactivate"),
    
    # Permisos
    path("permisos/", PermisoListView.as_view(), name="permiso_list"),
    path("permisos/nuevo/", PermisoCreateView.as_view(), name="permiso_create"),
    path("permisos/<int:pk>/editar/", PermisoUpdateView.as_view(), name="permiso_update"),
    path("permisos/<int:pk>/toggle/", permiso_inactivate, name="permiso_inactivate"),
    
    # Roles
    path("roles/", RolListView.as_view(), name="rol_list"),
    path("roles/nuevo/", RolCreateView.as_view(), name="rol_create"),
    path("roles/<int:pk>/editar/", RolUpdateView.as_view(), name="rol_update"),
    path("roles/<int:pk>/toggle/", rol_inactivate, name="rol_inactivate"),
]
