# bodega/urls.py
from django.urls import path
from .views import (
    HomeView,
    PersonaListView, PersonaCreateView, PersonaUpdateView, persona_inactivate,
)

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),

    # Personas
    path('personas/', PersonaListView.as_view(), name='persona_list'),
    path('personas/nueva/', PersonaCreateView.as_view(), name='persona_create'),
    path('personas/<int:pk>/editar/', PersonaUpdateView.as_view(), name='persona_update'),
    path('personas/<int:pk>/toggle/', persona_inactivate, name='persona_inactivate'),
]
