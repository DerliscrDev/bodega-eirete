# bodega/views.py (agregados para Persona)
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from .models import Persona
from .forms import PersonaForm
from .decorators import permiso_requerido
from django.contrib.auth.mixins import LoginRequiredMixin

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'bodega/home.html'

@method_decorator(permiso_requerido('ver_persona'), name='dispatch')
class PersonaListView(ListView):
    model = Persona
    template_name = "bodega/persona_list.html"
    context_object_name = "personas"
    paginate_by = 20

    def get_queryset(self):
        qs = Persona.objects.all()
        q = (self.request.GET.get('q') or '').strip()
        if q:
            qs = qs.filter(
                Q(cedula__icontains=q) |
                Q(nombre__icontains=q) |
                Q(apellido__icontains=q)
            )
        return qs.order_by('apellido', 'nombre', 'id')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = (self.request.GET.get('q') or '').strip()
        ctx['total'] = Persona.objects.count()
        ctx['filtrados'] = getattr(ctx.get('paginator'), 'count', len(ctx.get('personas', [])))
        return ctx

@method_decorator(permiso_requerido('crear_persona'), name='dispatch')
class PersonaCreateView(CreateView):
    model = Persona
    form_class = PersonaForm
    template_name = "bodega/persona_form.html"
    success_url = reverse_lazy('persona_list')

    def form_valid(self, form):
        # activo siempre True por defecto
        form.instance.activo = True
        messages.success(self.request, "Persona creada correctamente.")
        return super().form_valid(form)

@method_decorator(permiso_requerido('editar_persona'), name='dispatch')
class PersonaUpdateView(UpdateView):
    model = Persona
    form_class = PersonaForm
    template_name = "bodega/persona_form.html"
    success_url = reverse_lazy('persona_list')

    def form_valid(self, form):
        messages.success(self.request, "Persona actualizada correctamente.")
        return super().form_valid(form)

@permiso_requerido('inactivar_persona')
def persona_inactivate(request, pk):
    p = get_object_or_404(Persona, pk=pk)
    p.activo = not p.activo
    p.save(update_fields=['activo'])
    messages.info(request, "Persona reactivada." if p.activo else "Persona inactivada.")
    return redirect('persona_list')
