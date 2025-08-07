from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class CategoriaProducto(models.Model):
    nombre      = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)
    activo      = models.BooleanField(default=True)

    class Meta:
        ordering        = ["nombre"]
        verbose_name    = "categoría"
        verbose_name_plural = "categorías"

    def __str__(self) -> str:
        return self.nombre


class Marca(models.Model):
    nombre = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering     = ["nombre"]
        verbose_name = "marca"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    codigo          = models.CharField("SKU / Código", max_length=30, unique=True)
    nombre          = models.CharField(max_length=120)
    categoria       = models.ForeignKey(CategoriaProducto, on_delete=models.PROTECT)
    marca           = models.ForeignKey(Marca, on_delete=models.PROTECT, null=True, blank=True)
    unidad_medida   = models.CharField(max_length=20, default="unidad")
    stock_minimo    = models.PositiveIntegerField(default=0)
    iva_porcentaje  = models.DecimalField("IVA %", max_digits=4, decimal_places=2, default=10)
    activo          = models.BooleanField(default=True)

    class Meta:
        ordering        = ["nombre"]
        verbose_name    = "producto"

    def __str__(self):
        return f"{self.codigo} – {self.nombre}"

    # --- precio vigente ---
    @property
    def precio_vigente(self):
        vigente = self.precios.filter(fecha_fin__isnull=True).first()
        return vigente.precio if vigente else None


class Precio(models.Model):
    producto     = models.ForeignKey(Producto, related_name="precios", on_delete=models.CASCADE)
    precio       = models.DecimalField(max_digits=12, decimal_places=0)
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin    = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["-fecha_inicio"]
        verbose_name = "histórico de precio"
        constraints = [
            models.UniqueConstraint(
                fields=["producto"],
                condition=models.Q(fecha_fin__isnull=True),
                name="unique_precio_vigente_producto",
            )
        ]

    def clean(self):
        # garantizar un único precio vigente por producto
        if self.fecha_fin is None:
            conflict = Precio.objects.filter(
                producto=self.producto,
                fecha_fin__isnull=True
            ).exclude(pk=self.pk)
            if conflict.exists():
                raise ValidationError("Ya existe un precio vigente para este producto.")

        # coherencia fechas
        if self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            raise ValidationError("La fecha fin debe ser posterior a la fecha inicio.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
