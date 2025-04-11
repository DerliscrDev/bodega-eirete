from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.views import View
from django.contrib.auth.views import PasswordResetConfirmView
from django.utils.decorators import method_decorator

from .models import Empleado, Usuario, Rol, Permiso, Producto, Movimiento
from .forms import EmpleadoForm, UsuarioForm, RolForm, PermisoForm, CambiarPasswordForm, ProductoForm, MovimientoForm
from django.contrib.auth.tokens import default_token_generator
from .decorators import permiso_requerido

# Vista Home
@login_required
def home(request):
    return render(request, 'bodega/home.html')

# --- Empleados ---
@permiso_requerido('crear_empleado')
def crear_empleado(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = EmpleadoForm()
    return render(request, 'bodega/empleado_form.html', {'form': form})

@method_decorator(permiso_requerido('ver_empleado'), name='dispatch')
class EmpleadoListView(LoginRequiredMixin, ListView):
    model = Empleado
    template_name = 'bodega/empleado_list.html'
    context_object_name = 'empleados'
    paginate_by = 10

    def get_queryset(self):
        queryset = Empleado.objects.all()
        busqueda = self.request.GET.get('buscar')
        if busqueda:
            queryset = queryset.filter(nombre__icontains=busqueda) | queryset.filter(apellido__icontains=busqueda)
        return queryset

@method_decorator(permiso_requerido('editar_empleado'), name='dispatch')
class EmpleadoUpdateView(LoginRequiredMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = 'bodega/empleado_form.html'
    success_url = reverse_lazy('empleado_list')

@method_decorator(permiso_requerido('inactivar_empleado'), name='dispatch')
class EmpleadoInactivateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        self.object = Empleado.objects.get(pk=kwargs['pk'])
        return render(request, 'bodega/empleado_confirm_inactivate.html', {'object': self.object})

    def post(self, request, *args, **kwargs):
        self.object = Empleado.objects.get(pk=kwargs['pk'])
        self.object.activo = not self.object.activo
        self.object.save()
        return redirect('empleado_list')

# --- Usuarios ---
@method_decorator(permiso_requerido('crear_usuario'), name='dispatch')
class UsuarioCreateView(LoginRequiredMixin, CreateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'bodega/usuario_form.html'
    success_url = reverse_lazy('usuario_list')

    def form_valid(self, form):
        usuario = form.save(commit=False)
        temp_password = get_random_string(length=8)
        usuario.password = make_password(temp_password)
        usuario.estado = 'activo'
        usuario.is_active = False
        usuario.save()
        form.save_m2m()

        # token = token_generator.make_token(usuario)
        token = default_token_generator.make_token(usuario)
        uid = urlsafe_base64_encode(force_bytes(usuario.pk))
        reset_url = self.request.build_absolute_uri(
            reverse('cambiar_password', kwargs={'uidb64': uid, 'token': token})
        )

        subject = 'Bienvenido a Bodega Eirete - Cambia tu contraseña'
        message = (
            f"Hola {usuario.username},\n\n"
            f"Se ha creado tu cuenta en Bodega Eirete.\n\n"
            f"Tu contraseña temporal es: {temp_password}\n\n"
            f"Por seguridad, ingresa en el siguiente enlace para cambiar tu contraseña:\n{reset_url}\n\n"
            f"Gracias."
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [usuario.email])
        return HttpResponseRedirect(self.success_url)

@method_decorator(permiso_requerido('ver_usuario'), name='dispatch')
class UsuarioListView(LoginRequiredMixin, ListView):
    model = Usuario
    template_name = 'bodega/usuario_list.html'
    context_object_name = 'usuarios'
    paginate_by = 10

    def get_queryset(self):
        queryset = Usuario.objects.select_related('empleado', 'rol')
        busqueda = self.request.GET.get('buscar')
        if busqueda:
            queryset = queryset.filter(
                username__icontains=busqueda
            ) | queryset.filter(email__icontains=busqueda)
        return queryset

@method_decorator(permiso_requerido('editar_usuario'), name='dispatch')
class UsuarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'bodega/usuario_form.html'
    success_url = reverse_lazy('usuario_list')

@method_decorator(permiso_requerido('inactivar_usuario'), name='dispatch')
class UsuarioInactivateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        self.object = Usuario.objects.get(pk=kwargs['pk'])
        return render(request, 'bodega/usuario_confirm_inactivate.html', {'object': self.object})

    def post(self, request, *args, **kwargs):
        self.object = Usuario.objects.get(pk=kwargs['pk'])
        self.object.estado = 'activo' if self.object.estado == 'inactivo' else 'inactivo'
        self.object.save()
        return redirect('usuario_list')

# --- Roles ---
@method_decorator(permiso_requerido('ver_rol'), name='dispatch')
class RolListView(LoginRequiredMixin, ListView):
    model = Rol
    template_name = 'bodega/rol_list.html'
    context_object_name = 'roles'
    paginate_by = 10

    def get_queryset(self):
        queryset = Rol.objects.all()
        busqueda = self.request.GET.get('buscar')
        if busqueda:
            queryset = queryset.filter(
                nombre__icontains=busqueda
            ) | queryset.filter(descripcion__icontains=busqueda)
        return queryset

@method_decorator(permiso_requerido('crear_rol'), name='dispatch')
class RolCreateView(LoginRequiredMixin, CreateView):
    model = Rol
    form_class = RolForm
    template_name = 'bodega/rol_form.html'
    success_url = reverse_lazy('rol_list')

@method_decorator(permiso_requerido('editar_rol'), name='dispatch')
class RolUpdateView(LoginRequiredMixin, UpdateView):
    model = Rol
    form_class = RolForm
    template_name = 'bodega/rol_form.html'
    success_url = reverse_lazy('rol_list')

@method_decorator(permiso_requerido('inactivar_rol'), name='dispatch')
class RolInactivateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        self.object = Rol.objects.get(pk=kwargs['pk'])
        return render(request, 'bodega/rol_confirm_inactivate.html', {'object': self.object})

    def post(self, request, *args, **kwargs):
        self.object = Rol.objects.get(pk=kwargs['pk'])
        self.object.activo = not self.object.activo
        self.object.save()
        return redirect('rol_list')

@method_decorator(permiso_requerido('editar_rol'), name='dispatch')
class RolAsignarPermisosView(LoginRequiredMixin, UpdateView):
    model = Rol
    form_class = RolForm
    template_name = 'bodega/rol_form.html'
    success_url = reverse_lazy('rol_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.permisos.set(form.cleaned_data['permisos'])
        return response

# --- Permisos ---
@method_decorator(permiso_requerido('ver_permiso'), name='dispatch')
class PermisoListView(LoginRequiredMixin, ListView):
    model = Permiso
    template_name = 'bodega/permiso_list.html'
    context_object_name = 'permisos'
    paginate_by = 10

    def get_queryset(self):
        queryset = Permiso.objects.all().order_by('id')
        busqueda = self.request.GET.get('buscar')
        if busqueda:
            queryset = queryset.filter(
                nombre__icontains=busqueda
            ) | queryset.filter(descripcion__icontains=busqueda)
        return queryset

@method_decorator(permiso_requerido('crear_permiso'), name='dispatch')
class PermisoCreateView(LoginRequiredMixin, CreateView):
    model = Permiso
    form_class = PermisoForm
    template_name = 'bodega/permiso_form.html'
    success_url = reverse_lazy('permiso_list')

@method_decorator(permiso_requerido('editar_permiso'), name='dispatch')
class PermisoUpdateView(LoginRequiredMixin, UpdateView):
    model = Permiso
    form_class = PermisoForm
    template_name = 'bodega/permiso_form.html'
    success_url = reverse_lazy('permiso_list')

@method_decorator(permiso_requerido('inactivar_permiso'), name='dispatch')
class PermisoInactivateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        self.object = Permiso.objects.get(pk=kwargs['pk'])
        return render(request, 'bodega/permiso_confirm_inactivate.html', {'object': self.object})

    def post(self, request, *args, **kwargs):
        self.object = Permiso.objects.get(pk=kwargs['pk'])
        self.object.activo = not self.object.activo
        self.object.save()
        return redirect('permiso_list')

class PrimerCambioPasswordView(PasswordResetConfirmView):
    template_name = 'bodega/cambiar_password.html'
    success_url = reverse_lazy('login')
    form_class = CambiarPasswordForm
    token_generator = default_token_generator

    def form_valid(self, form):
        response = super().form_valid(form)
        self.user.is_active = True
        self.user.save()
        return response

@method_decorator(permiso_requerido('ver_producto'), name='dispatch')
class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'bodega/producto_list.html'
    context_object_name = 'productos'
    paginate_by = 10

    def get_queryset(self):
        queryset = Producto.objects.all().order_by('nombre')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(nombre__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


@method_decorator(permiso_requerido('crear_producto'), name='dispatch')
class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'bodega/producto_form.html'
    success_url = reverse_lazy('producto_list')

@method_decorator(permiso_requerido('editar_producto'), name='dispatch')
class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'bodega/producto_form.html'
    success_url = reverse_lazy('producto_list')

@method_decorator(permiso_requerido('inactivar_producto'), name='dispatch')
class ProductoInactivateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        self.object = Producto.objects.get(pk=kwargs['pk'])
        return render(request, 'bodega/producto_confirm_inactivate.html', {'object': self.object})

    def post(self, request, *args, **kwargs):
        self.object = Producto.objects.get(pk=kwargs['pk'])
        self.object.activo = not self.object.activo
        self.object.save()
        return redirect('producto_list')

@method_decorator(permiso_requerido('ver_movimiento'), name='dispatch')
class MovimientoListView(LoginRequiredMixin, ListView):
    model = Movimiento
    template_name = 'bodega/movimiento_list.html'
    context_object_name = 'movimientos'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('producto', 'realizado_por').order_by('-fecha')
        buscar = self.request.GET.get("buscar")
        if buscar:
            queryset = queryset.filter(producto__nombre__icontains=buscar)
        return queryset

@method_decorator(permiso_requerido('crear_movimiento'), name='dispatch')
class MovimientoCreateView(LoginRequiredMixin, CreateView):
    model = Movimiento
    form_class = MovimientoForm
    template_name = 'bodega/movimiento_form.html'
    success_url = reverse_lazy('movimiento_list')

    def form_valid(self, form):
        movimiento = form.save(commit=False)
        movimiento.realizado_por = self.request.user
        producto = movimiento.producto

        # Actualiza stock
        if movimiento.tipo == 'entrada':
            producto.stock += movimiento.cantidad
        elif movimiento.tipo == 'salida':
            producto.stock -= movimiento.cantidad

        producto.save()
        movimiento.save()
        return redirect(self.success_url)
