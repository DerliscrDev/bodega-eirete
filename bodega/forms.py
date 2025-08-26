# bodega/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import capfirst
from .models import Persona, Empleado

class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ["cedula", "nombre", "apellido"]  # 'activo' no es editable
        widgets = {
            "cedula": forms.TextInput(attrs={"class": "form-control", "placeholder": "Cédula"}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre"}),
            "apellido": forms.TextInput(attrs={"class": "form-control", "placeholder": "Apellido"}),
        }
        labels = {
            "cedula": "Cédula",
            "nombre": "Nombre",
            "apellido": "Apellido",
        }

    def clean_nombre(self):
        v = self.cleaned_data.get("nombre", "").strip()
        return capfirst(v)

    def clean_apellido(self):
        v = self.cleaned_data.get("apellido", "").strip()
        return capfirst(v)


class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        # Incluye campos de Persona + Empleado
        fields = [
            # Persona
            "cedula", "nombre", "apellido",
            # Empleado
            "genero", "fecha_nacimiento", "grupo_sanguineo",
            "telefono", "email",
            "direccion", "barrio", "ciudad", "departamento", "pais", "codigo_postal",
            "fecha_contratacion", "cargo", "sucursal",
            # "fecha_baja", "motivo_baja",  # podés exponerlos si querés administrar bajas desde el form
        ]
        widgets = {
            "cedula": forms.TextInput(attrs={"class": "form-control", "placeholder": "Cédula"}),
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellido": forms.TextInput(attrs={"class": "form-control"}),
            "genero": forms.Select(attrs={"class": "form-select"}),
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "grupo_sanguineo": forms.Select(attrs={"class": "form-select"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "+595..."}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "barrio": forms.TextInput(attrs={"class": "form-control"}),
            "ciudad": forms.TextInput(attrs={"class": "form-control"}),
            "departamento": forms.TextInput(attrs={"class": "form-control"}),
            "pais": forms.TextInput(attrs={"class": "form-control"}),
            "codigo_postal": forms.TextInput(attrs={"class": "form-control", "placeholder": "(opcional)"}),
            "fecha_contratacion": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "cargo": forms.Select(attrs={"class": "form-select"}),
            "sucursal": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "cedula": "Cédula",
            "nombre": "Nombre",
            "apellido": "Apellido",
            "genero": "Género",
            "fecha_nacimiento": "Fecha de nacimiento",
            "grupo_sanguineo": "Grupo sanguíneo",
            "telefono": "Teléfono",
            "email": "Email",
            "direccion": "Dirección",
            "barrio": "Barrio",
            "ciudad": "Ciudad",
            "departamento": "Departamento",
            "pais": "País",
            "codigo_postal": "Código postal (opcional)",
            "fecha_contratacion": "Fecha de contratación",
            "cargo": "Cargo",
            "sucursal": "Sucursal",
        }

    def clean_nombre(self):
        return capfirst(self.cleaned_data.get("nombre", "").strip())

    def clean_apellido(self):
        return capfirst(self.cleaned_data.get("apellido", "").strip())

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        # el modelo ya lo tiene unique, esto es sólo por UX
        if email and Empleado.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError("Ya existe un empleado con este email.")
        return email
