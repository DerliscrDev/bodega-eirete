from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import redirect, render, get_object_or_404

from .models import Producto, Precio
from .forms  import ProductoForm, PrecioFormSet


class ProductoListView(LoginRequiredMixin, ListView):
    model         = Producto
    template_name = "catalogo/producto_list.html"
    paginate_by   = 25

    # 1.  Filtro por búsqueda y categoría
    def get_queryset(self):
        qs = (Producto.objects
              .select_related("categoria", "marca")
              .prefetch_related("precios"))
        q  = self.request.GET.get("q")
        cat = self.request.GET.get("categoria")
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(codigo__icontains=q))
        if cat:
            qs = qs.filter(categoria_id=cat)
        return qs
    
    # 2.  ← ←  AQUÍ añadimos categorías al contexto
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categorias"] = CategoriaProducto.objects.filter(activo=True)
        return ctx

class ProductoCreateView(LoginRequiredMixin, CreateView):
    model         = Producto
    form_class    = ProductoForm
    template_name = "catalogo/producto_form.html"
    success_url   = reverse_lazy("producto_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["formset"] = kwargs.get("formset",
                           PrecioFormSet(prefix="precio"))
        return ctx

    def form_valid(self, form):
        context  = self.get_context_data()
        formset  = PrecioFormSet(self.request.POST, prefix="precio")
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            messages.success(self.request, "Producto creado correctamente.")
            return redirect(self.success_url)
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model         = Producto
    form_class    = ProductoForm
    template_name = "catalogo/producto_form.html"
    success_url   = reverse_lazy("producto_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx["formset"] = PrecioFormSet(
                self.request.POST,
                instance=self.object,
                prefix="precio"
            )
        else:
            ctx["formset"] = PrecioFormSet(
                instance=self.object,
                prefix="precio"
            )
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx["formset"]
        if formset.is_valid():
            self.object = form.save()
            formset.save()
            messages.success(self.request, "Producto actualizado.")
            return redirect(self.success_url)
        return self.render_to_response(ctx)

import openpyxl
from django.http import HttpResponse
from django.utils.timezone import localdate
from django.views import View


class ProductoExportView(LoginRequiredMixin, View):
    def get(self, request):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Productos"
        ws.append(["Código", "Nombre", "Categoría", "Marca",
                   "Precio vigente", "IVA %", "Stock mínimo"])

        for p in Producto.objects.select_related("categoria", "marca"):
            ws.append([
                p.codigo, p.nombre,
                p.categoria.nombre,
                p.marca.nombre if p.marca else "",
                p.precio_vigente or "",
                p.iva_porcentaje,
                p.stock_minimo,
            ])

        resp = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        resp["Content-Disposition"] = (
            f'attachment; filename=productos_{localdate()}.xlsx'
        )
        wb.save(resp)
        return resp
