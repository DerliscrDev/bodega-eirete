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




# from django import forms
# from django.contrib.auth.forms import SetPasswordForm
# from .models import (
#     Empleado, Usuario, Rol, Permiso, Producto, Movimiento, Proveedor, OrdenCompra, DetalleOrdenCompra, Cliente,
#     Almacen, Inventario, CategoriaProducto, Pedido, DetallePedido, Factura, DetalleFactura  
# )
# from django.forms import inlineformset_factory
# from django.utils.decorators import method_decorator


# # EmpleadoForm con campo cargo como select de roles
# class EmpleadoForm(forms.ModelForm):
#     class Meta:
#         model = Empleado
#         fields = ['nombre', 'apellido', 'direccion', 'telefono', 'email', 'fecha_contratacion', 'cargo', 'activo']
#         widgets = {
#             'nombre': forms.TextInput(attrs={'class': 'form-control'}),
#             'apellido': forms.TextInput(attrs={'class': 'form-control'}),
#             'direccion': forms.TextInput(attrs={'class': 'form-control'}),
#             'telefono': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#             'fecha_contratacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
#             'cargo': forms.Select(attrs={'class': 'form-control'}),
#             'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }

# # UsuarioForm sin cambios especiales
# class UsuarioForm(forms.ModelForm):
#     class Meta:
#         model = Usuario
#         fields = ['username', 'email', 'estado', 'empleado', 'rol']
#         widgets = {
#             'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de Usuario'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
#             'estado': forms.Select(attrs={'class': 'form-control'}),
#             'empleado': forms.Select(attrs={'class': 'form-control'}),
#             'rol': forms.Select(attrs={'class': 'form-control'}),
#         }

# # Para el cambio de contraseña inicial
# class CambiarPasswordForm(SetPasswordForm):
#     pass

# # RolForm con permisos activos como checkboxes
# class RolForm(forms.ModelForm):
#     permisos = forms.ModelMultipleChoiceField(
#         queryset=Permiso.objects.filter(activo=True),
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )

#     class Meta:
#         model = Rol
#         fields = ['nombre', 'descripcion', 'permisos']
#         widgets = {
#             'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Rol'}),
#             'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
#         }

# # PermisoForm con campo URL
# class PermisoForm(forms.ModelForm):
#     class Meta:
#         model = Permiso
#         fields = ['nombre', 'descripcion', 'url', 'activo']
#         widgets = {
#             'nombre': forms.TextInput(attrs={'class': 'form-control'}),
#             'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
#             'url': forms.TextInput(attrs={'class': 'form-control'}),
#             'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }

# class ProductoForm(forms.ModelForm):
#     class Meta:
#         model = Producto
#         fields = ['nombre', 'descripcion', 'codigo', 'precio', 'stock', 'activo']
#         widgets = {
#             'nombre': forms.TextInput(attrs={'class': 'form-control'}),
#             'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
#             'codigo': forms.TextInput(attrs={'class': 'form-control'}),
#             'precio': forms.NumberInput(attrs={'class': 'form-control'}),
#             'stock': forms.NumberInput(attrs={'class': 'form-control'}),
#             'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }

# class MovimientoForm(forms.ModelForm):
#     class Meta:
#         model = Movimiento
#         fields = ['producto', 'tipo', 'cantidad', 'observacion']
#         widgets = {
#             'producto': forms.Select(attrs={'class': 'form-control'}),
#             'tipo': forms.Select(attrs={'class': 'form-control'}),
#             'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
#             'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
#         }

# class ProveedorForm(forms.ModelForm):
#     class Meta:
#         model = Proveedor
#         fields = ['nombre', 'ruc', 'direccion', 'telefono', 'email', 'activo']
#         widgets = {
#             'nombre': forms.TextInput(attrs={'class': 'form-control'}),
#             'ruc': forms.TextInput(attrs={'class': 'form-control'}),
#             'direccion': forms.TextInput(attrs={'class': 'form-control'}),
#             'telefono': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#             'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }

# class OrdenCompraForm(forms.ModelForm):
#     class Meta:
#         model = OrdenCompra
#         fields = ['proveedor', 'estado', 'observacion']
#         widgets = {
#             'proveedor': forms.Select(attrs={'class': 'form-control'}),
#             'estado': forms.Select(attrs={'class': 'form-control'}),
#             'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#         }

# class DetalleOrdenCompraForm(forms.ModelForm):
#     class Meta:
#         model = DetalleOrdenCompra
#         fields = ['producto', 'cantidad', 'precio_unitario']
#         widgets = {
#             'producto': forms.Select(attrs={'class': 'form-control'}),
#             'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
#             'precio_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
#         }

# class ClienteForm(forms.ModelForm):
#     class Meta:
#         model = Cliente
#         fields = ['nombre', 'apellido', 'direccion', 'telefono', 'email', 'activo']
#         widgets = {
#             'nombre': forms.TextInput(attrs={'class': 'form-control'}),
#             'apellido': forms.TextInput(attrs={'class': 'form-control'}),
#             'direccion': forms.TextInput(attrs={'class': 'form-control'}),
#             'telefono': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#             'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }

# class AlmacenForm(forms.ModelForm):
#     class Meta:
#         model = Almacen
#         fields = ['nombre', 'direccion', 'descripcion', 'activo']
#         widgets = {
#             'nombre': forms.TextInput(attrs={'class': 'form-control'}),
#             'direccion': forms.TextInput(attrs={'class': 'form-control'}),
#             'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
#             'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }

# class CategoriaProductoForm(forms.ModelForm):
#     class Meta:
#         model = CategoriaProducto
#         fields = ['nombre', 'descripcion', 'activo']
#         widgets = {
#             'nombre': forms.TextInput(attrs={'class': 'form-control'}),
#             'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
#             'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }

# class PedidoForm(forms.ModelForm):
#     class Meta:
#         model = Pedido
#         fields = ['cliente', 'estado', 'observacion']

# class DetallePedidoForm(forms.ModelForm):
#     class Meta:
#         model = DetallePedido
#         fields = ['producto', 'cantidad', 'precio_unitario']

# DetallePedidoFormSet = inlineformset_factory(
#     Pedido,
#     DetallePedido,
#     form=DetallePedidoForm,
#     extra=1,
#     can_delete=True
# )

# class FacturaForm(forms.ModelForm):
#     class Meta:
#         model = Factura
#         fields = ['cliente', 'estado', 'observacion']
#         widgets = {
#             'cliente': forms.Select(attrs={'class': 'form-control'}),
#             'estado': forms.Select(attrs={'class': 'form-control'}),
#             'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#         }

# class DetalleFacturaForm(forms.ModelForm):
#     class Meta:
#         model = DetalleFactura
#         fields = ['producto', 'cantidad', 'precio_unitario']
#         widgets = {
#             'producto': forms.Select(attrs={'class': 'form-control'}),
#             'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
#             'precio_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
#         }
