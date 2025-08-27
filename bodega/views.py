# bodega/views.py (agregados para Persona)
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from .models import Persona, Permiso, Rol
from .forms import PersonaForm, PermisoForm, RolForm
from .decorators import permiso_requerido
from django.contrib.auth.mixins import LoginRequiredMixin

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'bodega/home.html'

# ====== PERSONA ======
@method_decorator(permiso_requerido("personas.ver"), name="dispatch")
class PersonaListView(LoginRequiredMixin, ListView):
    model = Persona
    template_name = "bodega/persona_list.html"
    context_object_name = "personas"
    paginate_by = 20

    def get_queryset(self):
        qs = Persona.objects.all()
        q = (self.request.GET.get("q") or "").strip()
        estado = (self.request.GET.get("estado") or "").strip()

        if q:
            qs = qs.filter(
                Q(cedula__icontains=q) |
                Q(nombre__icontains=q) |
                Q(apellido__icontains=q)
            )

        if estado == "activos":
            qs = qs.filter(activo=True)
        elif estado == "inactivos":
            qs = qs.filter(activo=False)

        return qs.order_by("apellido", "nombre", "id")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = (self.request.GET.get("q") or "").strip()
        ctx["estado"] = (self.request.GET.get("estado") or "").strip()
        return ctx

@method_decorator(permiso_requerido("personas.crear"), name="dispatch")
class PersonaCreateView(LoginRequiredMixin, CreateView):
    model = Persona
    form_class = PersonaForm
    template_name = "bodega/persona_form.html"
    success_url = reverse_lazy("persona_list")

    def form_valid(self, form):
        # 'activo' es editable=False en el modelo → viene True por defecto
        messages.success(self.request, "Persona creada correctamente.")
        return super().form_valid(form)

@method_decorator(permiso_requerido("personas.editar"), name="dispatch")
class PersonaUpdateView(LoginRequiredMixin, UpdateView):
    model = Persona
    form_class = PersonaForm
    template_name = "bodega/persona_form.html"
    success_url = reverse_lazy("persona_list")

    def form_valid(self, form):
        messages.success(self.request, "Persona actualizada correctamente.")
        return super().form_valid(form)

@permiso_requerido("personas.inactivar")
def persona_inactivate(request, pk):
    p = get_object_or_404(Persona, pk=pk)
    p.activo = not p.activo
    p.save(update_fields=["activo"])
    messages.info(request, "Persona reactivada." if p.activo else "Persona inactivada.")
    return redirect("persona_list")

# ====== PERMISOS ======
@method_decorator(permiso_requerido("permisos.ver"), name="dispatch")
class PermisoListView(ListView):
    model = Permiso
    template_name = "bodega/permiso_list.html"
    context_object_name = "permisos"
    paginate_by = 7

    def get_queryset(self):
        qs = Permiso.objects.all().order_by("modulo", "accion", "codigo", "id")
        q = (self.request.GET.get("q") or "").strip()
        estado = (self.request.GET.get("estado") or "").strip()

        if q:
            qs = qs.filter(
                Q(codigo__icontains=q) |
                Q(nombre__icontains=q) |
                Q(url_name__icontains=q)
            )

        if estado == "activos":
            qs = qs.filter(activo=True)
        elif estado == "inactivos":
            qs = qs.filter(activo=False)

        return qs

@method_decorator(permiso_requerido("permisos.crear"), name="dispatch")
class PermisoCreateView(LoginRequiredMixin, CreateView):
    model = Permiso
    form_class = PermisoForm
    template_name = "bodega/permiso_form.html"
    success_url = reverse_lazy("permiso_list")

@method_decorator(permiso_requerido("permisos.editar"), name="dispatch")
class PermisoUpdateView(UpdateView):
    model = Permiso
    form_class = PermisoForm
    template_name = "bodega/permiso_form.html"
    success_url = reverse_lazy("permiso_list")

    def form_valid(self, form):
        messages.success(self.request, "Permiso actualizado correctamente.")
        return super().form_valid(form)

@permiso_requerido("permisos.inactivar")
def permiso_inactivate(request, pk):
    p = get_object_or_404(Permiso, pk=pk)
    p.activo = not p.activo
    p.save(update_fields=["activo"])
    messages.info(request, "Permiso reactivado." if p.activo else "Permiso inactivado.")
    return redirect("permiso_list")

@method_decorator(permiso_requerido("roles.ver"), name="dispatch")
class RolListView(LoginRequiredMixin, ListView):
    model = Rol
    template_name = "bodega/rol_list.html"
    context_object_name = "roles"
    paginate_by = 20

    def get_queryset(self):
        qs = Rol.objects.all().order_by("nombre", "id")
        q = (self.request.GET.get("q") or "").strip()
        estado = (self.request.GET.get("estado") or "").strip()
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
        if estado == "activos":
            qs = qs.filter(activo=True)
        elif estado == "inactivos":
            qs = qs.filter(activo=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = (self.request.GET.get("q") or "").strip()
        ctx["estado"] = (self.request.GET.get("estado") or "").strip()
        return ctx

@method_decorator(permiso_requerido("roles.crear"), name="dispatch")
class RolCreateView(LoginRequiredMixin, CreateView):
    model = Rol
    form_class = RolForm
    template_name = "bodega/rol_form.html"
    success_url = reverse_lazy("rol_list")

    def form_valid(self, form):
        messages.success(self.request, "Rol creado correctamente.")
        return super().form_valid(form)

@method_decorator(permiso_requerido("roles.editar"), name="dispatch")
class RolUpdateView(LoginRequiredMixin, UpdateView):
    model = Rol
    form_class = RolForm
    template_name = "bodega/rol_form.html"
    success_url = reverse_lazy("rol_list")

    def form_valid(self, form):
        messages.success(self.request, "Rol actualizado correctamente.")
        return super().form_valid(form)

@permiso_requerido("roles.inactivar")
def rol_inactivate(request, pk):
    r = get_object_or_404(Rol, pk=pk)
    r.activo = not r.activo
    r.save(update_fields=["activo"])
    messages.info(request, "Rol reactivado." if r.activo else "Rol inactivado.")
    return redirect("rol_list")