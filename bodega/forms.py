# forms.py actualizado con herencia desde Persona
from django import forms
from django.forms import inlineformset_factory, DateInput
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import ValidationError
from .models import (
    Empleado, Usuario, Rol, Permiso, Producto, Movimiento, Proveedor, OrdenCompra, DetalleOrdenCompra,
    Cliente, Almacen, Inventario, CategoriaProducto, Pedido, DetallePedido, Factura, DetalleFactura,
    Caja, MovimientoCaja, TipoProducto
)

class EmpleadoForm(forms.ModelForm):
    # Datepickers nativos
    fecha_contratacion = forms.DateField(widget=DateInput(attrs={"type": "date"}))
    fecha_nacimiento = forms.DateField(widget=DateInput(attrs={"type": "date"}), required=False)

    # Hacemos “activo” una selección obligatoria (Sí/No) para que cuente como “requerido”
    ACTIVO_CHOICES = (("True", "Sí"), ("False", "No"))
    activo = forms.TypedChoiceField(
        choices=ACTIVO_CHOICES,
        coerce=lambda v: v == "True",
        widget=forms.RadioSelect,
        required=True,
    )

    class Meta:
        model = Empleado
        fields = [
            # Persona
            'nombre', 'apellido', 'genero', 'fecha_nacimiento',
            'documento_tipo', 'documento_num', 'ruc',
            'direccion', 'barrio', 'ciudad', 'departamento',
            'pais', 'codigo_postal', 'telefono', 'email',
            # Empleado
            'cedula', 'fecha_contratacion', 'sucursal',
            # Estado
            'activo',
        ]
        widgets = {
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'documento_tipo': forms.Select(attrs={'class': 'form-select'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'barrio': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'sucursal': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Por requerimiento: TODO requerido excepto codigo_postal
        for name, field in self.fields.items():
            field.required = (name != 'codigo_postal')

        # Sucursal (en modelo es null=True), pero aquí lo forzamos a requerido
        self.fields['sucursal'].required = True

        # Valor inicial de “activo” (Sí)
        if not self.instance.pk:
            self.fields['activo'].initial = "True"
        else:
            self.fields['activo'].initial = "True" if self.instance.activo else "False"

    # Validaciones para feedback claro (evitar IntegrityError genérico)
    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if not email:
            raise ValidationError("El email es obligatorio.")
        qs = Empleado.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Este email ya está registrado.")
        return email

    def clean_cedula(self):
        ced = (self.cleaned_data.get('cedula') or '').strip()
        if not ced:
            raise ValidationError("La cédula es obligatoria.")
        qs = Empleado.objects.filter(cedula=ced)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Esta cédula ya está registrada.")
        return ced

# class EmpleadoForm(forms.ModelForm):
#     class Meta:
#         model = Empleado
#         fields = ['nombre', 'apellido', 'cedula', 'direccion', 'telefono', 'email',
#                   'fecha_contratacion', 'sucursal', 'activo']

#     def clean_email(self):
#         email = (self.cleaned_data.get('email') or '').strip().lower() or None
#         if email:
#             qs = Empleado.objects.filter(email__iexact=email)
#             if self.instance.pk:
#                 qs = qs.exclude(pk=self.instance.pk)
#             if qs.exists():
#                 raise ValidationError("Este email ya está registrado.")
#         return email

#     def clean_cedula(self):
#         ced = (self.cleaned_data.get('cedula') or '').strip()
#         if not ced:
#             return ced
#         qs = Empleado.objects.filter(cedula=ced)
#         if self.instance.pk:
#             qs = qs.exclude(pk=self.instance.pk)
#         if qs.exists():
#             raise ValidationError("Esta cédula ya está registrada.")
#         return ced

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nombre', 'apellido', 'direccion', 'telefono', 'email',
            'condicion_venta', 'limite_credito', 'activo'
        ]

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
        fields = [
            'nombre', 'descripcion', 'marca', 'categoria',
            'codigo', 'unidad_medida', 'tipo_bebida',
            'precio_compra', 'margen_ganancia', 'iva',
            'stock_minimo', 'fecha_vencimiento',
            'proveedor', 'activo'
        ]


class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['producto', 'almacen', 'tipo', 'cantidad', 'observacion']

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'ruc', 'direccion', 'telefono', 'email', 'activo']

class OrdenCompraForm(forms.ModelForm):
    fecha_entrega = forms.DateField(
        widget=DateInput(attrs={'type': 'date'}),  # genera <input type="date">
        input_formats=['%Y-%m-%d']  # asegura el formato correcto
    )
    class Meta:
        model = OrdenCompra
        fields = ['proveedor', 'almacen_destino', 'nro_factura', 'fecha_entrega', 'estado', 'observacion']

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
        fields = ['nombre', 'activo']

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

DetalleOrdenCompraFormSet = inlineformset_factory(
    OrdenCompra,
    DetalleOrdenCompra,
    form=DetalleOrdenCompraForm,
    extra=0,
    can_delete=True
)

class CambiarPasswordForm(SetPasswordForm):
    pass

class CajaForm(forms.ModelForm):
    class Meta:
        model = Caja
        fields = ['monto_inicial']

class MovimientoCajaForm(forms.ModelForm):
    class Meta:
        model = MovimientoCaja
        fields = ['tipo', 'descripcion', 'monto']

class TipoProductoForm(forms.ModelForm):
    class Meta:
        model = TipoProducto
        fields = ['nombre', 'categoria', 'activo']
