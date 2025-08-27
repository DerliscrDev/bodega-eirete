import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import capfirst
from django.utils import timezone
from .models import Persona, Permiso, Rol, MODULOS, ACCIONES

CODIGO_REGEX = re.compile(r"^[a-z]+(\.[a-z_]+)$")  # modulo.accion (minúsculas, _ permitido en accion)
URLNAME_REGEX = re.compile(r"^[a-z0-9_]+$") 
DIGITOS_RE = re.compile(r'^\d+$')# nombre de url Django recomendado

class PermisoForm(forms.ModelForm):
    # Usamos campos DateTime explícitos para manejar el formato del input HTML5
    vigente_desde = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        input_formats=["%Y-%m-%dT%H:%M"],
    )
    vigente_hasta = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        input_formats=["%Y-%m-%dT%H:%M"],
    )
    
    class Meta:
        model = Permiso
        fields = [
            "codigo", "nombre",
            "modulo", "accion",
            "url_name",
        ]
        widgets = {
            "codigo": forms.TextInput(attrs={"class": "form-control", "placeholder": "permisos.crear"}),
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Crear permisos"}),
            "modulo": forms.Select(attrs={"class": "form-select"}),
            "accion": forms.Select(attrs={"class": "form-select"}),
            "url_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "permiso_create"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _split_codigo(self, codigo: str):
        if "." not in codigo:
            raise ValidationError("El código debe tener formato modulo.accion (ej.: personas.ver).")
        return codigo.split(".", 1)

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

        # validar rango usando la fecha de alta REAL de la instancia
        d = getattr(self.instance, "vigente_desde", None)

        # consistencia con el código
        codigo = cleaned.get("codigo")
        if codigo:
            m, a = self._split_codigo(codigo)
            if not cleaned.get("modulo"):
                cleaned["modulo"] = m
            elif str(cleaned["modulo"]) != str(m):
                self.add_error("modulo", f"Debe coincidir con el código: '{m}'.")
            if not cleaned.get("accion"):
                cleaned["accion"] = a
            elif str(cleaned["accion"]) != str(a):
                self.add_error("accion", f"Debe coincidir con el código: '{a}'.")
        return cleaned

    
    def save(self, commit=True):
        obj = super().save(commit=False)
        # sincronizar módulo/acción desde el código
        m, a = self._split_codigo(obj.codigo)
        obj.modulo, obj.accion = m, a
        if not obj.pk:
            obj.activo = True
        if commit:
            obj.save()
        return obj
    
class PermisoMultipleChoice(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        # Muestra el código y el nombre (ej.: permisos.crear — Crear permiso)
        return f"{obj.codigo} — {obj.nombre}"

class RolForm(forms.ModelForm):
    permisos = PermisoMultipleChoice(
        queryset=Permiso.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            "class": "form-select",   # <- sin size, Tom Select lo transforma en dropdown
        }),
        help_text="Seleccioná uno o más permisos."
    )

    class Meta:
        model = Rol
        fields = ["nombre", "descripcion", "permisos"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Administrador"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Rol con acceso total"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["permisos"].queryset = (
            Permiso.objects.filter(activo=True).order_by("modulo", "accion", "codigo")
        )

class PersonaForm(forms.ModelForm):
    class Meta:
        model = Persona
        fields = ["cedula", "nombre", "apellido"]   # 'activo' no es editable
        widgets = {
            "cedula": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Cédula (solo números)",
                # UX: teclado numérico en móviles, y patrón de dígitos
                "inputmode": "numeric",
                "pattern": r"\d*",
            }),
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre"}),
            "apellido": forms.TextInput(attrs={"class": "form-control", "placeholder": "Apellido"}),
        }
        labels = {"cedula": "Cédula", "nombre": "Nombre", "apellido": "Apellido"}

    def clean_cedula(self):
        v = (self.cleaned_data.get("cedula") or "").strip()
        if not DIGITOS_RE.fullmatch(v):
            raise ValidationError("La cédula debe contener solo números (sin puntos ni guiones).")
        if Persona.objects.exclude(pk=self.instance.pk).filter(cedula=v).exists():
            raise ValidationError("Ya existe una persona con esta cédula.")
        return v

    def clean_nombre(self):
        return capfirst((self.cleaned_data.get("nombre") or "").strip())

    def clean_apellido(self):
        return capfirst((self.cleaned_data.get("apellido") or "").strip())


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
