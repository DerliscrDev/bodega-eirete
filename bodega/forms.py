from django import forms
from .models import Empleado, Usuario, Rol, Permiso
from django.contrib.auth.forms import SetPasswordForm

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = '__all__'

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'estado', 'empleado', 'rol']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de Usuario'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'empleado': forms.Select(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
        }

class CambiarPasswordForm(SetPasswordForm):  # Para cambiar la contraseña al primer login
    pass

class RolForm(forms.ModelForm):
    permisos = forms.ModelMultipleChoiceField(
        queryset=Permiso.objects.filter(activo=True),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Rol
        fields = ['nombre', 'descripcion', 'permisos']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Rol'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
        }

class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permiso
        fields = '__all__'






# # bodega/forms.py
# from django import forms
# from .models import Empleado, Usuario, Rol, Permiso

# class EmpleadoForm(forms.ModelForm):
#     class Meta:
#         model = Empleado
#         fields = ['nombre', 'apellido', 'direccion', 'telefono', 'email', 'fecha_contratacion', 'cargo', 'salario']
#         widgets = {
#             'fecha_contratacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
#             'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellido'}),
#             'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
#             'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
#             'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cargo'}),
#             'salario': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Salario'}),
#         }

# class UsuarioForm(forms.ModelForm):
#     class Meta:
#         model = Usuario
#         # Excluimos el campo password para que se genere automáticamente
#         fields = ['username', 'email', 'estado', 'empleado']
#         widgets = {
#             'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de Usuario'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
#             'estado': forms.Select(attrs={'class': 'form-control'}),
#             'empleado': forms.Select(attrs={'class': 'form-control'}),
#         }


# class RolForm(forms.ModelForm):
#     class Meta:
#         model = Rol
#         fields = ['nombre', 'descripcion']
#         widgets = {
#             'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Rol'}),
#             'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
#         }

# class PermisoForm(forms.ModelForm):
#     class Meta:
#         model = Permiso
#         fields = ['nombre', 'descripcion']
#         widgets = {
#             'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Permiso'}),
#             'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
#         }
