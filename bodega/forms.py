# forms.py actualizado con herencia desde Persona
from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import SetPasswordForm
from .models import (
    Empleado, Usuario, Rol, Permiso, Producto, Movimiento, Proveedor, OrdenCompra, DetalleOrdenCompra,
    Cliente, Almacen, Inventario, CategoriaProducto, Pedido, DetallePedido, Factura, DetalleFactura
)

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'apellido', 'cedula', 'direccion', 'telefono', 'email', 'fecha_contratacion', 'cargo', 'sucursal', 'activo']

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'documento', 'direccion', 'telefono', 'email', 'activo']

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'estado', 'empleado', 'rol']

class RolForm(forms.ModelForm):
    permisos = forms.ModelMultipleChoiceField(
        queryset=Permiso.objects.filter(activo=True),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    class Meta:
        model = Rol
        fields = ['nombre', 'descripcion', 'permisos']

class PermisoForm(forms.ModelForm):
    class Meta:
        model = Permiso
        fields = ['nombre', 'descripcion', 'url', 'activo']

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'codigo', 'precio', 'stock', 'unidad_medida', 'iva', 'marca', 'activo']

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['producto', 'almacen', 'tipo', 'cantidad', 'observacion']

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'ruc', 'direccion', 'telefono', 'email', 'activo']

class OrdenCompraForm(forms.ModelForm):
    class Meta:
        model = OrdenCompra
        fields = ['proveedor', 'nro_factura', 'fecha_entrega', 'estado', 'observacion']

class DetalleOrdenCompraForm(forms.ModelForm):
    class Meta:
        model = DetalleOrdenCompra
        fields = ['producto', 'cantidad', 'precio_unitario']

class AlmacenForm(forms.ModelForm):
    class Meta:
        model = Almacen
        fields = ['nombre', 'direccion', 'descripcion', 'activo']

class CategoriaProductoForm(forms.ModelForm):
    class Meta:
        model = CategoriaProducto
        fields = ['nombre', 'descripcion', 'activo']

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'estado', 'observacion']

class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad', 'precio_unitario']

DetallePedidoFormSet = inlineformset_factory(
    Pedido,
    DetallePedido,
    form=DetallePedidoForm,
    extra=1,
    can_delete=True
)

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['cliente', 'nro_factura', 'timbrado', 'condicion_venta', 'estado', 'observacion']

class DetalleFacturaForm(forms.ModelForm):
    class Meta:
        model = DetalleFactura
        fields = ['producto', 'cantidad', 'precio_unitario', 'iva_aplicado']

DetalleFacturaFormSet = inlineformset_factory(
    Factura,
    DetalleFactura,
    form=DetalleFacturaForm,
    extra=1,
    can_delete=True
)

class CambiarPasswordForm(SetPasswordForm):
    pass