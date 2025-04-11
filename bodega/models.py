from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model

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

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    codigo = models.CharField(max_length=50, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    stock = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

Usuario = get_user_model()
    
class Movimiento(models.Model):
    TIPO_CHOICES = (
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    )

    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True, null=True)
    realizado_por = models.ForeignKey('Usuario', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo.title()} - {self.producto.nombre} ({self.cantidad})"

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=50, blank=True, null=True)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class OrdenCompra(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('recibido', 'Recibido'),
        ('cancelado', 'Cancelado'),
    )

    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Orden #{self.pk} - {self.proveedor.nombre}"


class DetalleOrdenCompra(models.Model):
    orden = models.ForeignKey(OrdenCompra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

class Cliente(Persona):
    activo = models.BooleanField(default=True)

    def __str__(self):
        return super().__str__()

class Almacen(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Inventario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('producto', 'almacen')

    def __str__(self):
        return f"{self.producto.nombre} - {self.almacen.nombre}"

class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
