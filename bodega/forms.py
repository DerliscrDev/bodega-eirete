import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import capfirst
from django.utils import timezone
from .models import Persona, Permiso, Rol, Empleado, MODULOS, ACCIONES

CODIGO_REGEX = re.compile(r"^[a-z]+(\.[a-z_]+)$")  # modulo.accion (minúsculas, _ permitido en accion)
URLNAME_REGEX = re.compile(r"^[a-z0-9_]+$") 
DIGITOS_RE = re.compile(r'^\d+$')# nombre de url Django recomendado
DOC_RE = re.compile(r'^[A-Za-z0-9]+$')

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
        fields = ["tipo_persona", "tipo_documento", "numero_de_documento",
                  "nombre", "apellido", "ruc_base", "ruc_dv"]
        widgets = {
            "tipo_persona": forms.Select(attrs={"class":"form-select"}),
            "tipo_documento": forms.Select(attrs={"class":"form-select"}),
            "numero_de_documento": forms.TextInput(attrs={
                "class":"form-control",
                "inputmode":"text", "pattern":"[A-Za-z0-9]+",
            }),
            "nombre": forms.TextInput(attrs={"class":"form-control"}),
            "apellido": forms.TextInput(attrs={"class":"form-control"}),
            "ruc_base": forms.TextInput(attrs={
                "class":"form-control", "placeholder":"RUC",
                "inputmode":"numeric", "pattern": r"\d+",
            }),
            "ruc_dv": forms.TextInput(attrs={
                "class":"form-control", "placeholder":"DV",
                "inputmode":"numeric", "pattern": r"\d",
            }),
        }
        labels = {
            "tipo_persona": "Tipo de persona",
            "tipo_documento": "Tipo de documento",
            "numero_de_documento": "Número de documento",
            "nombre": "Nombre/s  / Razón social",
            "apellido": "Apellido/s",
            "ruc_base": "RUC",
            "ruc_dv": "DV",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Siempre obligatorios
        self.fields["tipo_persona"].required = True
        self.fields["nombre"].required = True
        self.fields["tipo_persona"].error_messages["required"] = "Seleccioná el tipo de persona."
        self.fields["nombre"].error_messages["required"] = "Ingresá el nombre."
        
        # Si es edición y es J pero tipo_documento viene vacío, prellenar
        if (self.instance and self.instance.pk and 
            getattr(self.instance, "tipo_persona", None) == "J" and
            not (self.initial.get("tipo_documento") or self.instance.tipo_documento)):
            self.initial["tipo_documento"] = "RUC"

        # Condicionales: NO required a nivel field
        for fname in ("tipo_documento", "numero_de_documento", "apellido", "ruc_base", "ruc_dv"):
            self.fields[fname].required = False
            self.fields[fname].error_messages["required"] = "Campo obligatorio."

    # normalizaciones
    def clean_nombre(self):
        return capfirst((self.cleaned_data.get("nombre") or "").strip())

    def clean_apellido(self):
        return capfirst((self.cleaned_data.get("apellido") or "").strip())

    def clean_numero_de_documento(self):
        v = (self.cleaned_data.get("numero_de_documento") or "").strip()
        if not v:
            return None
        if not DOC_RE.fullmatch(v):
            raise ValidationError("El número de documento debe ser alfanumérico (sin espacios ni símbolos).")
        if Persona.objects.exclude(pk=self.instance.pk).filter(numero_de_documento=v).exists():
            raise ValidationError("Ya existe una persona con este número de documento.")
        return v

    def clean_ruc_base(self):
        v = (self.cleaned_data.get("ruc_base") or "").strip()
        if not v:
            return None
        if not DIGITOS_RE.fullmatch(v):
            raise ValidationError("El RUC debe contener solo dígitos.")
        return v

    def clean_ruc_dv(self):
        v = (self.cleaned_data.get("ruc_dv") or "").strip()
        if not v:
            return None
        if not DIGITOS_RE.fullmatch(v) or len(v) != 1:
            raise ValidationError("El dígito verificador (DV) debe ser un solo dígito.")
        return v

    # def clean(self):
    #     cleaned = super().clean()
    #     tipo = cleaned.get("tipo_persona")
    #     tdoc = cleaned.get("tipo_documento")
    #     doc  = cleaned.get("numero_de_documento")
    #     ape  = cleaned.get("apellido")
    #     rucb = cleaned.get("ruc_base")
    #     rucd = cleaned.get("ruc_dv")

    #     if not tipo:
    #         # self.add_error("tipo_persona", "Seleccioná el tipo de persona.")
    #         return cleaned

    #     if tipo == 'F':
    #         # Tipo de documento válido para F: CI, PAS u OTRO (RUC no corresponde acá)
    #         if tdoc not in ('CI', 'PAS', 'OTRO'):
    #             self.add_error("tipo_documento", "Elegí CI, Pasaporte u Otro documento.")

    #         # Requeridos para F
    #         if not doc:
    #             self.add_error("numero_de_documento", "Ingresá el número de documento.")
    #         if not ape:
    #             self.add_error("apellido", "Ingresá el apellido.")

    #         # RUC para F: OPCIONAL, pero si lo cargan debe ser válido y único
    #         if rucb or rucd:
    #             if not rucb:
    #                 self.add_error("ruc_base", "Ingresá el RUC (solo números).")
    #             if not rucd:
    #                 self.add_error("ruc_dv", "Ingresá el DV.")
    #             if rucb and rucd:
    #                 if Persona.objects.exclude(pk=self.instance.pk).filter(ruc_base=rucb, ruc_dv=rucd).exists():
    #                     self.add_error("ruc_base", "Ya existe una persona con este RUC.")
    #                     self.add_error("ruc_dv", "Revisá el dígito verificador.")

    #     elif tipo == 'J':
    #         # Para J el documento no aplica, y el tipo_documento debe ser RUC
    #         if tdoc != 'RUC':
    #             self.add_error("tipo_documento", "Para persona jurídica el tipo de documento debe ser RUC.")
    #         if not rucb:
    #             self.add_error("ruc_base", "Ingresá el RUC (solo números).")
    #         if not rucd:
    #             self.add_error("ruc_dv", "Ingresá el DV.")
    #         cleaned["numero_de_documento"] = None
    #         cleaned["apellido"] = ""

    #         if rucb and rucd:
    #             if Persona.objects.exclude(pk=self.instance.pk).filter(ruc_base=rucb, ruc_dv=rucd).exists():
    #                 self.add_error("ruc_base", "Ya existe una persona con este RUC.")
    #                 self.add_error("ruc_dv", "Revisá el dígito verificador.")

        return cleaned

class BaseEmpleadoForm(forms.ModelForm):
    persona_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Empleado
        fields = [
            # Persona base (requeridos)
            "numero_de_documento", "nombre", "apellido",
            # Empleado
            "genero", "fecha_nacimiento", "grupo_sanguineo",
            "telefono", "email",
            "direccion", "barrio", "ciudad", "departamento", "pais",
            "fecha_contratacion", "cargo",
        ]
        widgets = {
            "numero_de_documento": forms.TextInput(attrs={"class":"form-control","placeholder":"Cédula (solo números)","inputmode":"numeric","pattern":r"\d*"}),
            "nombre": forms.TextInput(attrs={"class":"form-control","placeholder":"Nombre"}),
            "apellido": forms.TextInput(attrs={"class":"form-control","placeholder":"Apellido"}),

            "genero": forms.Select(attrs={"class":"form-select"}),
            "fecha_nacimiento": forms.DateInput(attrs={"type":"date","class":"form-control"}),
            "grupo_sanguineo": forms.Select(attrs={"class":"form-select"}),

            "telefono": forms.TextInput(attrs={"class":"form-control","placeholder":"+595..."}),
            "email": forms.EmailInput(attrs={"class":"form-control"}),

            "direccion": forms.TextInput(attrs={"class":"form-control"}),
            "barrio": forms.TextInput(attrs={"class":"form-control"}),
            "ciudad": forms.TextInput(attrs={"class":"form-control"}),
            "departamento": forms.TextInput(attrs={"class":"form-control"}),
            "pais": forms.TextInput(attrs={"class":"form-control"}),

            "fecha_contratacion": forms.DateInput(attrs={"type":"date","class":"form-control"}),
            "cargo": forms.Select(attrs={"class":"form-select"}),
        }
        labels = {
            "numero_de_documento":"Número de documento","nombre":"Nombre","apellido":"Apellido",
            "genero":"Género","fecha_nacimiento":"Fecha de nacimiento","grupo_sanguineo":"Grupo sanguíneo",
            "telefono":"Teléfono","email":"Email",
            "direccion":"Dirección","barrio":"Barrio","ciudad":"Ciudad","departamento":"Departamento","pais":"País",
            "fecha_contratacion":"Fecha de contratación","cargo":"Cargo (rol)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cargo"].queryset = Rol.objects.filter(activo=True).order_by("nombre")
        for f in self.fields.values():
            f.required = True

        # ---- Bloquear cédula/nombre/apellido si:
        # - se seleccionó una Persona desde el buscador (persona_id en POST)
        # - o es edición (instance.pk existe)
        persona_id = (self.data.get("persona_id")
                      or self.initial.get("persona_id")
                      or (self.instance.pk if getattr(self.instance, "pk", None) else None))
        if persona_id:
            self._make_readonly("numero_de_documento", "nombre", "apellido")
            
    def _make_readonly(self, *field_names):
        for name in field_names:
            w = self.fields[name].widget
            # readonly mantiene el envío del valor (a diferencia de disabled)
            attrs = getattr(w, "attrs", {})
            attrs.update({"readonly": "readonly", "tabindex": "-1", "class": (attrs.get("class","") + " bg-light")})
            w.attrs = attrs
    
    # ----- Validaciones que fuerzan los datos de Persona si viene persona_id
    def _persona_from_form(self):
        pid = self.data.get("persona_id") or self.cleaned_data.get("persona_id")
        if not pid:
            return None
        try:
            return Persona.objects.get(pk=pid)
        except Persona.DoesNotExist:
            return None


    # Validaciones base Persona
    def clean_numero_de_documento(self):  # ← renombrado
        v = (self.cleaned_data.get("numero_de_documento") or "").strip()
        if not DOC_RE.fullmatch(v):
            raise ValidationError("El número de documento debe ser alfanumérico (sin espacios ni símbolos).")
        p = self._persona_from_form()
        if p:
            return p.numero_de_documento  # ← fuerza lo que viene de Persona
        if Persona.objects.exclude(pk=self.instance.pk).filter(numero_de_documento=v).exists():
            raise ValidationError("Ya existe una persona con este documento. Usá el buscador para seleccionarla.")
        return v

    def clean_nombre(self):
        p = self._persona_from_form()
        if p:
            return p.nombre
        return capfirst((self.cleaned_data.get("nombre") or "").strip())

    def clean_apellido(self):
        p = self._persona_from_form()
        if p:
            return p.apellido
        return capfirst((self.cleaned_data.get("apellido") or "").strip())


class EmpleadoCreateForm(BaseEmpleadoForm):
    """Alta: sin fecha/motivo de baja, fecha_alta se setea sola."""


class EmpleadoUpdateForm(BaseEmpleadoForm):
    """Edición: permite setear baja si corresponde."""
    class Meta(BaseEmpleadoForm.Meta):
        fields = BaseEmpleadoForm.Meta.fields + ["fecha_baja", "motivo_baja"]
        widgets = dict(BaseEmpleadoForm.Meta.widgets, **{
            "fecha_baja": forms.DateInput(attrs={"type":"date","class":"form-control"}),
            "motivo_baja": forms.TextInput(attrs={"class":"form-control"}),
        })
        labels = dict(BaseEmpleadoForm.Meta.labels, **{
            "fecha_baja":"Fecha de baja", "motivo_baja":"Motivo de baja",
        })