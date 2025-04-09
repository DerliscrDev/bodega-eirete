from django.contrib.auth.models import AbstractUser
from django.db import models

# Modelo base para Persona
class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# Empleado hereda de Persona
class Empleado(Persona):
    fecha_contratacion = models.DateField()
    cargo = models.ForeignKey('Rol', on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return super().__str__()

# Permiso
class Permiso(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()
    url = models.CharField(max_length=255, blank=True, null=True)  # Nuevo campo
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

# Rol con permisos
class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()
    permisos = models.ManyToManyField(Permiso, related_name="roles")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

# Usuario extendido
class Usuario(AbstractUser):
    empleado = models.OneToOneField(Empleado, on_delete=models.CASCADE, null=True, blank=True)
    ESTADO_CHOICES = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    )
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='activo')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username
