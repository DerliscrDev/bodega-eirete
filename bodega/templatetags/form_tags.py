from django import template

register = template.Library()

@register.filter(name="add_class")
def add_class(field, css):
    """
    Agrega clases CSS al widget sin perder las existentes.
    Uso: {{ form.campo|add_class:"form-control is-invalid" }}
    """
    attrs = field.field.widget.attrs.copy()
    prev = attrs.get("class", "")
    attrs["class"] = (prev + " " + css).strip()
    return field.as_widget(attrs=attrs)
