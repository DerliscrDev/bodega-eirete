from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

# Helpers
TELEFONO_REGEX = RegexValidator(
    r'^\+?\d{7,15}$',
    'Use formato internacional sin espacios, ej: +595981123456'
)

CEDULA_SOLO_DIGITOS = RegexValidator(
    r'^\d+$',
    'La cédula debe contener solo números (sin puntos, guiones ni espacios).'
)

GENERO = (
    ('M', 'Masculino'),
    ('F', 'Femenino'),
)

TIPO_DOC = (
    ('CI', 'Cédula'),
    ('RUC', 'RUC'),
    ('OTRO', 'Otro'),
)

CONDICION_VENTA = (
    ('contado', 'Contado'),
    ('credito', 'Crédito'),
)

GRUPO_SANGUINEO = (
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-'),
)

ACCIONES = (
    ("ver", "Ver/Consultar"),
    ("crear", "Crear"),
    ("editar", "Editar"),
    ("inactivar", "Inactivar"),
)


MODULOS = (
    ("home", "Inicio"),
    ("personas", "Personas"),
    ("empleados", "Empleados"),
    ("permisos", "Permisos"),
    ("roles", "Roles"),
)

class Permiso(models.Model):
    codigo = models.CharField(
    max_length=50,
    unique=True,
    validators=[RegexValidator(
        r'^[a-z]+(\.[a-z_]+)$',
        'Usa formato modulo.accion en minúsculas (ej.: personas.ver).'
        )],
    )
    nombre = models.CharField(max_length=80)
    modulo = models.CharField(max_length=30, choices=MODULOS, db_index=True)
    accion = models.CharField(max_length=20, choices=ACCIONES, db_index=True)
    url_name = models.CharField(max_length=120, blank=True, null=True,
                                help_text="Nombre de URL de Django (opcional)")
    vigente_desde = models.DateTimeField(auto_now_add=True, editable=False)# ← ahora con hora
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bodega_permiso"
        ordering = ["modulo", "nombre"]
        indexes = [
            models.Index(fields=["modulo", "accion"], name="idx_perm_mod_acc"),
            models.Index(fields=["url_name"], name="idx_perm_urlname"),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"
    
class Rol(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    permisos = models.ManyToManyField('Permiso', related_name='roles', blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bodega_rol"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

class Persona(models.Model):
    cedula   = models.CharField(
        max_length=7,
        unique=True,
        db_index=True,
        validators=[CEDULA_SOLO_DIGITOS],
    )
    nombre   = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    activo   = models.BooleanField(default=True, db_index=True, editable=False)

    class Meta:
        db_table = 'bodega_persona'
        ordering = ['apellido', 'nombre']
        indexes = [
            models.Index(fields=['apellido', 'nombre'], name='idx_persona_nombre'),
        ]

    def __str__(self):
        return f"{self.nombre} {self.apellido} — CI {self.cedula}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}".strip()

    def save(self, *args, **kwargs):
        if self.nombre:
            self.nombre = self.nombre.strip().title()
        if self.apellido:
            self.apellido = self.apellido.strip().title()
        if self.cedula:
            self.cedula = self.cedula.strip()
        super().save(*args, **kwargs)

class Empleado(Persona):
    genero = models.CharField(max_length=1, choices=GENERO)
    fecha_nacimiento = models.DateField()
    grupo_sanguineo = models.CharField(max_length=3, choices=GRUPO_SANGUINEO)
    telefono = models.CharField(max_length=20, validators=[TELEFONO_REGEX])
    email = models.EmailField(unique=True)
    direccion = models.CharField(max_length=255)
    barrio = models.CharField(max_length=120)
    ciudad = models.CharField(max_length=120)
    departamento = models.CharField(max_length=120)
    pais = models.CharField(max_length=120, default='Paraguay')
    fecha_contratacion = models.DateField()
    cargo = models.ForeignKey(
        'Rol',
        on_delete=models.PROTECT,
        related_name='empleados_cargo',
    )
    fecha_alta = models.DateTimeField(default=timezone.now, editable=False)  # PY local al mostrar
    fecha_baja = models.DateField(blank=True, null=True)
    motivo_baja = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'bodega_empleado'
        ordering = ['-activo', 'apellido', 'nombre']
        indexes = [
            models.Index(fields=['fecha_contratacion'], name='idx_empleado_fecha_ingreso'),
            models.Index(fields=['email'], name='idx_empleado_email'),
        ]

    def __str__(self):
        return f"{self.apellido}, {self.nombre} — CI {self.cedula}"

class Usuario(AbstractUser):
    # ahora: varios roles por usuario
    roles = models.ManyToManyField(Rol, blank=True, related_name='usuarios')
    ESTADO_CHOICES = (('activo', 'Activo'), ('inactivo', 'Inactivo'))
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='activo')

    def has_custom_permission(self, codigo_permiso: str) -> bool:
        if self.is_superuser or self.is_staff:
            return True
        # ¿algún rol del usuario trae ese permiso activo?
        from django.apps import apps
        Permiso = apps.get_model('bodega', 'Permiso')
        return Permiso.objects.filter(
            roles__usuarios=self,
            codigo=codigo_permiso,
            activo=True
        ).exists()

# --- Cargo ligado a roles mínimos ---
class Cargo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    # roles mínimos que implica ocupar este cargo
    default_roles = models.ManyToManyField(Rol, blank=True, related_name='cargos')
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'bodega_cargo'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre



# # -----------------
# # Catálogo de cargos
# # -----------------
# class Cargo(models.Model):
#     nombre = models.CharField(max_length=100, unique=True)
#     descripcion = models.TextField(blank=True, null=True)
#     activo = models.BooleanField(default=True)

#     class Meta:
#         db_table = 'bodega_cargo'
#         ordering = ['nombre']

#     def __str__(self):
#         return self.nombre


# # -----------------
# # Empleado (hereda de Persona)
# # -----------------
class Empleado(Persona):
    # Datos personales extra
    genero = models.CharField(max_length=1, choices=GENERO, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    grupo_sanguineo = models.CharField(max_length=3, choices=GRUPO_SANGUINEO, null=True, blank=True)

    # Contacto / domicilio
    telefono = models.CharField(max_length=20, validators=[TELEFONO_REGEX])
    email = models.EmailField(unique=True)
    direccion = models.CharField(max_length=255)
    barrio = models.CharField(max_length=120)
    ciudad = models.CharField(max_length=120)
    departamento = models.CharField(max_length=120)
    pais = models.CharField(max_length=120, default='Paraguay')
    codigo_postal = models.CharField(max_length=12, blank=True, null=True)  # único opcional

    # Laboral
    fecha_contratacion = models.DateField()
    cargo = models.ForeignKey(Cargo, on_delete=models.SET_NULL, null=True, blank=True, related_name='empleados')
    fecha_baja = models.DateField(blank=True, null=True)
    motivo_baja = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'bodega_empleado'
        ordering = ['-activo', 'apellido', 'nombre']
        indexes = [
            models.Index(fields=['fecha_contratacion'], name='idx_empleado_fecha_ingreso'),
            models.Index(fields=['email'], name='idx_empleado_email'),
        ]

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        return super().save(*args, **kwargs)