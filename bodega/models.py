from django.contrib.auth.models import AbstractUser
from django.db import models

# Base: Persona
class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# Empleado
class Empleado(Persona):
    fecha_contratacion = models.DateField()
    cargo = models.CharField(max_length=100)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

# Usuario extendido
class Usuario(AbstractUser):
    empleado = models.OneToOneField('Empleado', on_delete=models.CASCADE, null=True, blank=True)
    ESTADO_CHOICES = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    )
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='activo')
    rol = models.ForeignKey('Rol', on_delete=models.SET_NULL, null=True, blank=True)  # 👈 Agrega esta línea

    def __str__(self):
        return self.username

# Rol y Permiso personalizados
class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class Permiso(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

# Relaciones
# En tu modelo Usuario (ya extendido de AbstractUser)
rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
Rol.permisos = models.ManyToManyField(Permiso, related_name="roles")










# # bodega/models.py
# from django.contrib.auth.models import AbstractUser
# from django.db import models

# # Modelo base para Persona
# class Persona(models.Model):
#     nombre = models.CharField(max_length=100)
#     apellido = models.CharField(max_length=100)
#     direccion = models.CharField(max_length=255)
#     telefono = models.CharField(max_length=20)
#     email = models.EmailField(unique=True)

#     def __str__(self):
#         return f"{self.nombre} {self.apellido}"

# # Empleado hereda de Persona
# class Empleado(Persona):
#     fecha_contratacion = models.DateField()
#     cargo = models.CharField(max_length=100)
#     salario = models.DecimalField(max_digits=10, decimal_places=2)
#     activo = models.BooleanField(default=True)  # Nuevo campo para borrado lógico

#     def __str__(self):
#         return super().__str__()

# class Usuario(AbstractUser):
#     # El modelo AbstractUser ya incluye username, email, password, last_login, is_active, etc.
#     empleado = models.OneToOneField(Empleado, on_delete=models.CASCADE, null=True, blank=True)
#     ESTADO_CHOICES = (
#         ('activo', 'Activo'),
#         ('inactivo', 'Inactivo'),
#     )
#     estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='activo')
#     # Puedes sobrescribir __str__ si lo deseas
#     def __str__(self):
#         return self.username

# # Modelo de Rol
# class Rol(models.Model):
#     nombre = models.CharField(max_length=50)
#     descripcion = models.TextField()

#     def __str__(self):
#         return self.nombre

# # Modelo de Permiso
# class Permiso(models.Model):
#     nombre = models.CharField(max_length=50)
#     descripcion = models.TextField()
#     activo = models.BooleanField(default=True)  # Campo para borrado lógico

#     def __str__(self):
#         return self.nombre
# # Relaciones ManyToMany
# Usuario.roles = models.ManyToManyField(Rol, related_name="usuarios")
# Rol.permisos = models.ManyToManyField(Permiso, related_name="roles")
