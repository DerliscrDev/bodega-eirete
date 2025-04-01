from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import (
    home,
    crear_empleado, EmpleadoListView, EmpleadoUpdateView, EmpleadoInactivateView,
    UsuarioListView, UsuarioCreateView, UsuarioUpdateView, UsuarioInactivateView,
    PrimerCambioPasswordView,
    RolListView, RolCreateView, RolUpdateView, RolDeleteView, RolAsignarPermisosView,
    PermisoListView, PermisoCreateView, PermisoUpdateView, PermisoInactivateView,
)

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='bodega/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('home/', home, name='home'),
    # Empleados:
    path('empleados/nuevo/', crear_empleado, name='empleado_create'),
    path('empleados/', EmpleadoListView.as_view(), name='empleado_list'),
    path('empleados/editar/<int:pk>/', EmpleadoUpdateView.as_view(), name='empleado_update'),
    path('empleados/inactivar/<int:pk>/', EmpleadoInactivateView.as_view(), name='empleado_inactivate'),
    # Usuarios:
    path('usuarios/', UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/nuevo/', UsuarioCreateView.as_view(), name='usuario_create'),
    path('usuarios/editar/<int:pk>/', UsuarioUpdateView.as_view(), name='usuario_update'),
    path('usuarios/inactivar/<int:pk>/', UsuarioInactivateView.as_view(), name='usuario_inactivate'),
    # Ruta para cambiar la contraseña inicial:
    path('usuarios/cambiar-password/<uidb64>/<token>/', PrimerCambioPasswordView.as_view(), name='cambiar_password'),
    # Roles:
    path('roles/', RolListView.as_view(), name='rol_list'),
    path('roles/nuevo/', RolCreateView.as_view(), name='rol_create'),
    path('roles/editar/<int:pk>/', RolUpdateView.as_view(), name='rol_update'),
    path('roles/eliminar/<int:pk>/', RolDeleteView.as_view(), name='rol_delete'),
    path('roles/permisos/<int:pk>/', RolAsignarPermisosView.as_view(), name='rol_asignar_permisos'),
    # Permisos:
    path('permisos/', PermisoListView.as_view(), name='permiso_list'),
    path('permisos/nuevo/', PermisoCreateView.as_view(), name='permiso_create'),
    path('permisos/editar/<int:pk>/', PermisoUpdateView.as_view(), name='permiso_update'),
    path('permisos/inactivar/<int:pk>/', PermisoInactivateView.as_view(), name='permiso_inactivate'),
]
