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
from .tokens import token_generator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import PasswordResetConfirmView
from .models import Empleado, Usuario, Rol, Permiso
from .forms import EmpleadoForm, UsuarioForm, RolForm, PermisoForm

# Vista Home
@login_required
def home(request):
    return render(request, 'bodega/home.html')

# --- Empleados ---
@login_required
def crear_empleado(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = EmpleadoForm()
    return render(request, 'bodega/empleado_form.html', {'form': form})

class EmpleadoListView(LoginRequiredMixin, ListView):
    model = Empleado
    template_name = 'bodega/empleado_list.html'
    context_object_name = 'empleados'

class EmpleadoUpdateView(LoginRequiredMixin, UpdateView):
    model = Empleado
    form_class = EmpleadoForm
    template_name = 'bodega/empleado_form.html'
    success_url = reverse_lazy('empleado_list')

class EmpleadoInactivateView(LoginRequiredMixin, DeleteView):
    model = Empleado
    template_name = 'bodega/empleado_confirm_delete.html'
    success_url = reverse_lazy('empleado_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        return redirect(self.success_url)

# --- Usuarios ---
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
        usuario.save()
        form.save_m2m()

        token = token_generator.make_token(usuario)
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
        recipient_email = usuario.email
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])

        return HttpResponseRedirect(self.success_url)

class UsuarioListView(LoginRequiredMixin, ListView):
    model = Usuario
    template_name = 'bodega/usuario_list.html'
    context_object_name = 'usuarios'

class UsuarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioForm
    template_name = 'bodega/usuario_form.html'
    success_url = reverse_lazy('usuario_list')

class UsuarioInactivateView(LoginRequiredMixin, DeleteView):
    model = Usuario
    template_name = 'bodega/usuario_confirm_delete.html'
    success_url = reverse_lazy('usuario_list')

    def get(self, request, *args, **kwargs):
        return redirect('usuario_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.estado = 'inactivo'
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

# --- Roles ---
class RolListView(LoginRequiredMixin, ListView):
    model = Rol
    template_name = 'bodega/rol_list.html'
    context_object_name = 'roles'

class RolCreateView(LoginRequiredMixin, CreateView):
    model = Rol
    form_class = RolForm
    template_name = 'bodega/rol_form.html'
    success_url = reverse_lazy('rol_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.permisos.set(form.cleaned_data['permisos'])
        return response

class RolUpdateView(LoginRequiredMixin, UpdateView):
    model = Rol
    form_class = RolForm
    template_name = 'bodega/rol_form.html'
    success_url = reverse_lazy('rol_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.permisos.set(form.cleaned_data['permisos'])
        return response

class RolDeleteView(LoginRequiredMixin, DeleteView):
    model = Rol
    template_name = 'bodega/rol_confirm_delete.html'
    success_url = reverse_lazy('rol_list')

# --- Permisos ---
class PermisoListView(LoginRequiredMixin, ListView):
    model = Permiso
    template_name = 'bodega/permiso_list.html'
    context_object_name = 'permisos'

class PermisoCreateView(LoginRequiredMixin, CreateView):
    model = Permiso
    form_class = PermisoForm
    template_name = 'bodega/permiso_form.html'
    success_url = reverse_lazy('permiso_list')

class PermisoUpdateView(LoginRequiredMixin, UpdateView):
    model = Permiso
    form_class = PermisoForm
    template_name = 'bodega/permiso_form.html'
    success_url = reverse_lazy('permiso_list')

class PermisoInactivateView(LoginRequiredMixin, DeleteView):
    model = Permiso
    template_name = 'bodega/permiso_confirm_delete.html'
    success_url = reverse_lazy('permiso_list')

    def get(self, request, *args, **kwargs):
        return redirect('permiso_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

# --- Cambio de contraseña inicial ---
from django.contrib.auth.forms import SetPasswordForm

class PrimerCambioPasswordView(PasswordResetConfirmView):
    template_name = 'bodega/cambiar_password.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('login')

    def get_token_generator(self):
        from .tokens import token_generator
        return token_generator

    def form_valid(self, form):
        response = super().form_valid(form)
        self.user.is_active = True
        self.user.save()
        return response











# # bodega/views.py
# from django.shortcuts import render, redirect
# from django.http import HttpResponseRedirect
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.hashers import make_password
# from django.utils.crypto import get_random_string
# from django.core.mail import send_mail
# from django.conf import settings
# from django.urls import reverse, reverse_lazy
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from .tokens import token_generator
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.views.generic import ListView, CreateView, UpdateView, DeleteView
# from .models import Empleado, Usuario, Rol, Permiso
# from .forms import EmpleadoForm, UsuarioForm, RolForm, PermisoForm
# from django.contrib.auth.views import PasswordResetConfirmView

# ## # # # # #  Nuevo
# from django.contrib.auth.forms import SetPasswordForm
# from django.contrib.auth.views import PasswordResetConfirmView

# class PrimerCambioPasswordView(PasswordResetConfirmView):
#     template_name = 'bodega/cambiar_password.html'
#     form_class = SetPasswordForm
#     success_url = reverse_lazy('login')
#     token_generator = token_generator  # ¡Este es el cambio clave!

#     def form_valid(self, form):
#         response = super().form_valid(form)
#         # Si usás estado lógico, podés marcarlo como activo (opcional)
#         self.user.is_active = True
#         self.user.save()
#         return response

# class RolCreateView(LoginRequiredMixin, CreateView):
#     model = Rol
#     form_class = RolForm
#     template_name = 'bodega/rol_form.html'
#     success_url = reverse_lazy('rol_list')

#     def form_valid(self, form):
#         response = super().form_valid(form)
#         self.object.permisos.set(form.cleaned_data['permisos'])
#         return response

# class RolUpdateView(LoginRequiredMixin, UpdateView):
#     model = Rol
#     form_class = RolForm
#     template_name = 'bodega/rol_form.html'
#     success_url = reverse_lazy('rol_list')

#     def form_valid(self, form):
#         response = super().form_valid(form)
#         self.object.permisos.set(form.cleaned_data['permisos'])
#         return response



# # # # # # # # # # # # # # # # # # # # # # 



# # Vista Home
# @login_required
# def home(request):
#     return render(request, 'bodega/home.html')

# # --- Empleados ---
# @login_required
# def crear_empleado(request):
#     if request.method == 'POST':
#         form = EmpleadoForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('home')
#     else:
#         form = EmpleadoForm()
#     return render(request, 'bodega/empleado_form.html', {'form': form})

# class EmpleadoListView(LoginRequiredMixin, ListView):
#     model = Empleado
#     template_name = 'bodega/empleado_list.html'
#     context_object_name = 'empleados'

# class EmpleadoUpdateView(LoginRequiredMixin, UpdateView):
#     model = Empleado
#     form_class = EmpleadoForm
#     template_name = 'bodega/empleado_form.html'
#     success_url = reverse_lazy('empleado_list')

# class EmpleadoInactivateView(LoginRequiredMixin, DeleteView):
#     model = Empleado
#     template_name = 'bodega/empleado_confirm_delete.html'  # Template mínimo para el proceso
#     success_url = reverse_lazy('empleado_list')

#     def delete(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         # Borrado lógico: se marca el empleado como inactivo
#         self.object.activo = False
#         self.object.save()
#         return redirect(self.success_url)

# # --- Usuarios ---
# class UsuarioCreateView(LoginRequiredMixin, CreateView):
#     model = Usuario
#     form_class = UsuarioForm
#     template_name = 'bodega/usuario_form.html'
#     success_url = reverse_lazy('usuario_list')

#     def form_valid(self, form):
#         usuario = form.save(commit=False)
#         # Genera una contraseña temporal de 8 caracteres
#         temp_password = get_random_string(length=8)
#         usuario.password = make_password(temp_password)
#         usuario.estado = 'activo'
#         usuario.save()
#         form.save_m2m()  # Guarda relaciones many-to-many

#         # Genera token y uid usando el token personalizado
#         token = token_generator.make_token(usuario)
#         uid = urlsafe_base64_encode(force_bytes(usuario.pk))

#         # Construir la URL absoluta para cambiar contraseña
#         reset_url = self.request.build_absolute_uri(
#             reverse('cambiar_password', kwargs={'uidb64': uid, 'token': token})
#         )

#         subject = 'Bienvenido a Bodega Eirete - Cambia tu contraseña'
#         message = (
#             f"Hola {usuario.username},\n\n"
#             f"Se ha creado tu cuenta en Bodega Eirete.\n\n"
#             f"Tu contraseña temporal es: {temp_password}\n\n"
#             f"Por seguridad, ingresa en el siguiente enlace para cambiar tu contraseña:\n{reset_url}\n\n"
#             f"Gracias."
#         )
#         recipient_email = usuario.email
#         send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])

#         return HttpResponseRedirect(self.success_url)

# class UsuarioListView(LoginRequiredMixin, ListView):
#     model = Usuario
#     template_name = 'bodega/usuario_list.html'
#     context_object_name = 'usuarios'

# class UsuarioUpdateView(LoginRequiredMixin, UpdateView):
#     model = Usuario
#     form_class = UsuarioForm
#     template_name = 'bodega/usuario_form.html'
#     success_url = reverse_lazy('usuario_list')

# class UsuarioInactivateView(LoginRequiredMixin, DeleteView):
#     model = Usuario
#     template_name = 'bodega/usuario_confirm_delete.html'
#     success_url = reverse_lazy('usuario_list')

#     def get(self, request, *args, **kwargs):
#         return redirect('usuario_list')

#     def delete(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         self.object.estado = 'inactivo'
#         self.object.save()
#         return HttpResponseRedirect(self.get_success_url())

# # --- Roles ---
# class RolListView(LoginRequiredMixin, ListView):
#     model = Rol
#     template_name = 'bodega/rol_list.html'
#     context_object_name = 'roles'

# # class RolCreateView(LoginRequiredMixin, CreateView):
# #     model = Rol
# #     form_class = RolForm
# #     template_name = 'bodega/rol_form.html'
# #     success_url = reverse_lazy('rol_list')

# # class RolUpdateView(LoginRequiredMixin, UpdateView):
# #     model = Rol
# #     form_class = RolForm
# #     template_name = 'bodega/rol_form.html'
# #     success_url = reverse_lazy('rol_list')

# class RolDeleteView(LoginRequiredMixin, DeleteView):
#     model = Rol
#     template_name = 'bodega/rol_confirm_delete.html'
#     success_url = reverse_lazy('rol_list')

# # --- Permisos ---
# class PermisoListView(LoginRequiredMixin, ListView):
#     model = Permiso
#     template_name = 'bodega/permiso_list.html'
#     context_object_name = 'permisos'

# class PermisoCreateView(LoginRequiredMixin, CreateView):
#     model = Permiso
#     form_class = PermisoForm
#     template_name = 'bodega/permiso_form.html'
#     success_url = reverse_lazy('permiso_list')

# class PermisoUpdateView(LoginRequiredMixin, UpdateView):
#     model = Permiso
#     form_class = PermisoForm
#     template_name = 'bodega/permiso_form.html'
#     success_url = reverse_lazy('permiso_list')

# class PermisoInactivateView(LoginRequiredMixin, DeleteView):
#     model = Permiso
#     template_name = 'bodega/permiso_confirm_delete.html'  # No se usará si se confirma mediante el modal
#     success_url = reverse_lazy('permiso_list')

#     def get(self, request, *args, **kwargs):
#         # Si se accede por GET directamente, redirige al listado
#         return redirect('permiso_list')

#     def delete(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         # Realizamos el borrado lógico: marcamos el permiso como inactivo
#         self.object.activo = False
#         self.object.save()
#         return HttpResponseRedirect(self.get_success_url())

# # class PrimerCambioPasswordView(PasswordResetConfirmView):
# #     template_name = 'bodega/cambiar_password.html'
# #     success_url = reverse_lazy('login')
    
# #     def get_token_generator(self):
# #         from .tokens import token_generator
# #         return token_generator
