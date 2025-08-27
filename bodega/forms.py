import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import capfirst
from .models import Persona, Permiso, MODULOS, ACCIONES

CODIGO_REGEX = re.compile(r"^[a-z]+(\.[a-z_]+)$")  # modulo.accion (minúsculas, _ permitido en accion)
URLNAME_REGEX = re.compile(r"^[a-z0-9_]+$")        # nombre de url Django recomendado

class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permiso
        fields = [
            "codigo", "nombre",
            "modulo", "accion",
            "url_name",
            "vigente_desde", "vigente_hasta",
            "activo",
        ]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control", "placeholder": "personas.ver"}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ver personas"}),
            "modulo": forms.Select(attrs={"class": "form-select"}),
            "accion": forms.Select(attrs={"class": "form-select"}),
            "url_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "persona_list"}),
            "vigente_desde": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "vigente_hasta": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # crear: oculto 'activo' y lo seteo True
        if not self.instance or not self.instance.pk:
            self.fields["activo"].initial = True
            self.fields["activo"].widget = forms.HiddenInput()

    # helpers
    def _split_codigo(self, codigo: str):
        if "." not in codigo:
            raise ValidationError("El código debe tener el formato modulo.accion (ej.: personas.ver).")
        modulo, accion = codigo.split(".", 1)
        return modulo, accion

    # validaciones campo a campo
    def clean_codigo(self):
        codigo = (self.cleaned_data.get("codigo") or "").strip().lower()
        if not CODIGO_REGEX.match(codigo):
            raise ValidationError("Formato inválido. Usa 'modulo.accion' en minúsculas (ej.: personas.ver).")
        if Permiso.objects.exclude(pk=self.instance.pk).filter(codigo=codigo).exists():
            raise ValidationError("Ya existe un permiso con este código.")
        return codigo

    def clean_url_name(self):
        url_name = (self.cleaned_data.get("url_name") or "").strip()
        if url_name and not URLNAME_REGEX.match(url_name):
            raise ValidationError("Usa minúsculas, números o '_' (ej.: persona_list).")
        return url_name

    # validaciones cruzadas
    def clean(self):
        cleaned = super().clean()
        d, h = cleaned.get("vigente_desde"), cleaned.get("vigente_hasta")
        if d and h and d > h:
            self.add_error("vigente_hasta", "La fecha 'Vigente hasta' debe ser mayor o igual a 'Vigente desde'.")

        codigo = cleaned.get("codigo")
        if codigo:
            modulo_from_code, accion_from_code = self._split_codigo(codigo)
            if not cleaned.get("modulo"):
                cleaned["modulo"] = modulo_from_code
            elif str(cleaned["modulo"]) != str(modulo_from_code):
                self.add_error("modulo", f"Debe coincidir con el código: '{modulo_from_code}'.")
            if not cleaned.get("accion"):
                cleaned["accion"] = accion_from_code
            elif str(cleaned["accion"]) != str(accion_from_code):
                self.add_error("accion", f"Debe coincidir con el código: '{accion_from_code}'.")
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        if not obj.pk:
            obj.activo = True
        modulo_from_code, accion_from_code = self._split_codigo(obj.codigo)
        obj.modulo = modulo_from_code
        obj.accion = accion_from_code
        if commit:
            obj.save()
        return obj


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


# class EmpleadoForm(forms.ModelForm):
#     class Meta:
#         model = Empleado
#         # Incluye campos de Persona + Empleado
#         fields = [
#             # Persona
#             "cedula", "nombre", "apellido",
#             # Empleado
#             "genero", "fecha_nacimiento", "grupo_sanguineo",
#             "telefono", "email",
#             "direccion", "barrio", "ciudad", "departamento", "pais", "codigo_postal",
#             "fecha_contratacion", "cargo", "sucursal",
#             # "fecha_baja", "motivo_baja",  # podés exponerlos si querés administrar bajas desde el form
#         ]
#         widgets = {
#             "cedula": forms.TextInput(attrs={"class": "form-control", "placeholder": "Cédula"}),
#             "nombre": forms.TextInput(attrs={"class": "form-control"}),
#             "apellido": forms.TextInput(attrs={"class": "form-control"}),
#             "genero": forms.Select(attrs={"class": "form-select"}),
#             "fecha_nacimiento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
#             "grupo_sanguineo": forms.Select(attrs={"class": "form-select"}),
#             "telefono": forms.TextInput(attrs={"class": "form-control", "placeholder": "+595..."}),
#             "email": forms.EmailInput(attrs={"class": "form-control"}),
#             "direccion": forms.TextInput(attrs={"class": "form-control"}),
#             "barrio": forms.TextInput(attrs={"class": "form-control"}),
#             "ciudad": forms.TextInput(attrs={"class": "form-control"}),
#             "departamento": forms.TextInput(attrs={"class": "form-control"}),
#             "pais": forms.TextInput(attrs={"class": "form-control"}),
#             "codigo_postal": forms.TextInput(attrs={"class": "form-control", "placeholder": "(opcional)"}),
#             "fecha_contratacion": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
#             "cargo": forms.Select(attrs={"class": "form-select"}),
#             "sucursal": forms.Select(attrs={"class": "form-select"}),
#         }
#         labels = {
#             "cedula": "Cédula",
#             "nombre": "Nombre",
#             "apellido": "Apellido",
#             "genero": "Género",
#             "fecha_nacimiento": "Fecha de nacimiento",
#             "grupo_sanguineo": "Grupo sanguíneo",
#             "telefono": "Teléfono",
#             "email": "Email",
#             "direccion": "Dirección",
#             "barrio": "Barrio",
#             "ciudad": "Ciudad",
#             "departamento": "Departamento",
#             "pais": "País",
#             "codigo_postal": "Código postal (opcional)",
#             "fecha_contratacion": "Fecha de contratación",
#             "cargo": "Cargo",
#             "sucursal": "Sucursal",
#         }

#     def clean_nombre(self):
#         return capfirst(self.cleaned_data.get("nombre", "").strip())

#     def clean_apellido(self):
#         return capfirst(self.cleaned_data.get("apellido", "").strip())

#     def clean_email(self):
#         email = (self.cleaned_data.get("email") or "").strip().lower()
#         # el modelo ya lo tiene unique, esto es sólo por UX
#         if email and Empleado.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
#             raise ValidationError("Ya existe un empleado con este email.")
#         return email
