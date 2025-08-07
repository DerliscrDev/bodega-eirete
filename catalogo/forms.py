from django import forms
from django.forms import inlineformset_factory
from .models import Producto, Precio


class ProductoForm(forms.ModelForm):
    class Meta:
        model  = Producto
        fields = [
            "codigo", "nombre", "categoria", "marca", "unidad_medida",
            "stock_minimo", "iva_porcentaje", "activo"
        ]


class PrecioForm(forms.ModelForm):
    class Meta:
        model  = Precio
        fields = ["precio", "fecha_inicio", "fecha_fin"]


PrecioFormSet = inlineformset_factory(
    parent_model   = Producto,
    model          = Precio,
    form           = PrecioForm,
    extra          = 1,
    can_delete     = False,
    max_num        = 1,           # solo cargamos / editamos el vigente
    validate_max   = True
)
