from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.db.models.functions import Lower
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from decimal import Decimal

# =========================
# Helpers / Choices
# =========================
TELEFONO_REGEX = RegexValidator(
    r'^\+?\d{7,15}$',
    'Use formato internacional sin espacios, ej: +595981123456'
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

# =========================
# Modelo base con trazas
# =========================
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True

# === BASE ===
class Persona(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    genero = models.CharField(max_length=1, choices=GENERO, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    documento_tipo = models.CharField(max_length=10, choices=TIPO_DOC, default='CI')
    documento_num = models.CharField(max_length=30, blank=True, null=True)
    ruc = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    barrio = models.CharField(max_length=120, blank=True, null=True)
    ciudad = models.CharField(max_length=120, blank=True, null=True)
    departamento = models.CharField(max_length=120, blank=True, null=True)
    pais = models.CharField(max_length=120, default='Paraguay')
    codigo_postal = models.CharField(max_length=12, blank=True, null=True)
    telefono = models.CharField(max_length=20, validators=[TELEFONO_REGEX], blank=True, null=True)
    email = models.EmailField(blank=True, null=True)  # unicidad case-insensitive con constraint abajo
    activo = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'bodega_persona'   # ajusta a tu realidad; si quieres que Django cree la tabla, deja managed=True por defecto
        # managed = False             # descomenta si ya tienes la tabla creada manualmente
        ordering = ['apellido', 'nombre']
        indexes = [
            models.Index(fields=['apellido', 'nombre'], name='idx_persona_nombre'),
            models.Index(fields=['ruc'], name='idx_persona_ruc'),
            models.Index(fields=['documento_tipo', 'documento_num'], name='idx_persona_doc'),
        ]
        constraints = [
            # Documento único por tipo cuando está informado
            models.UniqueConstraint(
                fields=['documento_tipo', 'documento_num'],
                condition=Q(documento_num__isnull=False),
                name='uq_persona_documento'
            ),
            # Email único case-insensitive cuando NO es NULL
            models.UniqueConstraint(
                Lower('email'),
                condition=Q(email__isnull=False),
                name='uq_persona_email_lower'
            ),
        ]

    def __str__(self):
        return self.nombre_completo

    @property
    def nombre_completo(self) -> str:
        base = f"{self.nombre or ''} {self.apellido or ''}".strip()
        return base or f"Persona #{self.pk}"

    def save(self, *args, **kwargs):
        # Normalizaciones suaves
        if self.nombre:
            self.nombre = self.nombre.strip().title()
        if self.apellido:
            self.apellido = self.apellido.strip().title()
        if self.documento_tipo:
            self.documento_tipo = self.documento_tipo.strip().upper()
        if self.email:
            self.email = self.email.strip().lower()
        if self.pk is None:          # solo al crear
            self.activo = True
        super().save(*args, **kwargs)

# === RRHH ===
class Empleado(Persona):
    cedula = models.CharField(max_length=20, unique=True)
    fecha_contratacion = models.DateField()
    sucursal = models.ForeignKey('Almacen', on_delete=models.SET_NULL, null=True, blank=True, related_name='empleados')
    fecha_baja = models.DateField(blank=True, null=True)
    motivo_baja = models.CharField(max_length=255, blank=True, null=True)
    # 'activo' ya lo hereda de Persona

    class Meta:
        db_table = 'bodega_empleado'   # si ya existe, podés usar managed=False
        managed = False
        ordering = ['-activo', 'apellido', 'nombre']
        indexes = [
            models.Index(fields=['fecha_contratacion'], name='idx_empleado_estado_fecha'),
            models.Index(fields=['cedula'], name='idx_empleado_cedula'),
        ]

class Cliente(Persona):
    condicion_venta = models.CharField(max_length=20, choices=CONDICION_VENTA, default='contado', db_index=True)
    limite_credito = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    # 'activo' ya lo hereda de Persona

    class Meta:
        db_table = 'bodega_cliente'    # si ya existe, podés usar managed=False
        managed = False
        ordering = ['-activo', 'apellido', 'nombre']
        indexes = [
            models.Index(fields=['condicion_venta'], name='idx_cliente_cond_venta'),
        ]
        
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
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class TipoProducto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE, related_name='tipos')
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.categoria.nombre})"

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    marca = models.CharField(max_length=100, blank=True)
    categoria = models.ForeignKey('CategoriaProducto', on_delete=models.SET_NULL, null=True, blank=True)

    # Datos logísticos y físicos
    codigo = models.CharField(max_length=50, unique=True, help_text="Código interno del producto")
    unidad_medida = models.CharField(max_length=50, default="unidad")  # Ej: botella, litro, caja
    volumen = models.FloatField(help_text="Contenido neto en mililitros", null=True, blank=True)

    # Información para bebidas alcohólicas
    tipo_bebida = models.CharField(
        max_length=50,
        choices=[
            ('vino', 'Vino'),
            ('cerveza', 'Cerveza'),
            ('otro', 'Otro'),
        ],
        blank=True
    )

    # Precios y tributación
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    margen_ganancia = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), help_text="Margen %")
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    iva = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('10.00'), help_text="IVA aplicado (%)")

    # Control de stock
    stock_minimo = models.PositiveIntegerField(default=0)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    proveedor = models.ForeignKey('Proveedor', on_delete=models.SET_NULL, null=True, blank=True)

    # Otros
    activo = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        """
        Calcula precio_venta = precio_compra * (1 + margen/100) * (1 + iva/100)
        Solo recalcula si hay precio_compra y margen definidos.
        """
        pc = Decimal(self.precio_compra or 0)
        mg = Decimal(self.margen_ganancia or 0) / Decimal('100')
        iva = Decimal(self.iva or 0) / Decimal('100')
        base = pc * (Decimal('1') + mg)
        self.precio_venta = (base * (Decimal('1') + iva)).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

# class Producto(models.Model):
#     UNIDADES = [
#         ("unidad", "Unidad"),
#         ("litros", "Litros"),
#         ("cajas", "Cajas"),
#     ]
#     IVA = [
#         ("exento", "Exento"),
#         ("5", "5%"),
#         ("10", "10%"),
#     ]

#     nombre = models.CharField(max_length=100)
#     descripcion = models.TextField(blank=True, null=True)
#     categoria = models.ForeignKey(CategoriaProducto, on_delete=models.SET_NULL, null=True, blank=True)
#     codigo = models.CharField(max_length=50, unique=True)
#     precio = models.DecimalField(max_digits=10, decimal_places=0)
#     stock = models.PositiveIntegerField(default=0)
#     unidad_medida = models.CharField(max_length=20, choices=UNIDADES, default='unidad')
#     iva = models.CharField(max_length=10, choices=IVA, default='10')
#     marca = models.CharField(max_length=100, blank=True, null=True)
#     activo = models.BooleanField(default=True)

#     def __str__(self):
#         return f"{self.nombre} ({self.codigo})"

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
    almacen_destino = models.ForeignKey('Almacen', on_delete=models.SET_NULL, null=True, blank=True)
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
    facturado = models.BooleanField(default=False)

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

class Caja(models.Model):
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    usuario_apertura = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='aperturas_caja')
    usuario_cierre = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='cierres_caja')
    monto_inicial = models.DecimalField(max_digits=12, decimal_places=2)
    monto_final = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    estado = models.CharField(max_length=10, choices=[('abierta', 'Abierta'), ('cerrada', 'Cerrada')], default='abierta')

    def __str__(self):
        return f"Caja {self.pk} - {self.estado}"


class MovimientoCaja(models.Model):
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=[('ingreso', 'Ingreso'), ('egreso', 'Egreso')])
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tipo.capitalize()} - {self.monto} Gs"
