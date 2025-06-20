from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model

# === BASE ===
class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# === RRHH ===
class Empleado(Persona):
    cedula = models.CharField(max_length=20, unique=True)
    fecha_contratacion = models.DateField()
    cargo = models.ForeignKey('Rol', on_delete=models.SET_NULL, null=True, blank=True)
    sucursal = models.ForeignKey('Almacen', on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)

class Cliente(Persona):
    documento = models.CharField(max_length=20, unique=True)
    activo = models.BooleanField(default=True)

# === SEGURIDAD ===
class Permiso(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()
    url = models.CharField(max_length=255, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()
    permisos = models.ManyToManyField(Permiso, related_name="roles")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    empleado = models.OneToOneField(Empleado, on_delete=models.CASCADE, null=True, blank=True)
    ESTADO_CHOICES = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    )
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='activo')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)

# === INVENTARIO ===
class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    UNIDADES = [
        ("unidad", "Unidad"),
        ("litros", "Litros"),
        ("cajas", "Cajas"),
    ]
    IVA = [
        ("exento", "Exento"),
        ("5", "5%"),
        ("10", "10%"),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.SET_NULL, null=True, blank=True)
    codigo = models.CharField(max_length=50, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=0)
    stock = models.PositiveIntegerField(default=0)
    unidad_medida = models.CharField(max_length=20, choices=UNIDADES, default='unidad')
    iva = models.CharField(max_length=10, choices=IVA, default='10')
    marca = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

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

class Movimiento(models.Model):
    TIPO_CHOICES = (
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    )

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True, null=True)
    realizado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tipo.title()} - {self.producto.nombre} ({self.cantidad})"

# === COMPRAS ===
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    ruc = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
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
    nro_factura = models.CharField(max_length=50, blank=True, null=True)
    fecha_entrega = models.DateField(blank=True, null=True)
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

# === VENTAS ===
class Pedido(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pedido #{self.pk} - {self.cliente}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

class Factura(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observacion = models.TextField(blank=True, null=True)
    nro_factura = models.CharField(max_length=50)
    timbrado = models.CharField(max_length=50)
    condicion_venta = models.CharField(max_length=20, choices=[('contado', 'Contado'), ('credito', 'Crédito')], default='contado')
    estado = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('pagada', 'Pagada'), ('anulada', 'Anulada')], default='pendiente')

    def __str__(self):
        return f"Factura #{self.id} - {self.cliente}"

class DetalleFactura(models.Model):
    IVA = [
        ("exento", "Exento"),
        ("5", "5%"),
        ("10", "10%")
    ]
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)
    iva_aplicado = models.CharField(max_length=10, choices=IVA, default='10')

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"
