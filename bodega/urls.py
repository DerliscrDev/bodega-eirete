from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    home,
    crear_empleado, EmpleadoListView, EmpleadoUpdateView, EmpleadoInactivateView,
    UsuarioListView, UsuarioCreateView, UsuarioUpdateView, UsuarioInactivateView,
    PrimerCambioPasswordView,
    RolListView, RolCreateView, RolUpdateView, RolInactivateView, RolAsignarPermisosView,
    PermisoListView, PermisoCreateView, PermisoUpdateView, PermisoInactivateView,
    ProductoListView, ProductoCreateView, ProductoUpdateView, ProductoInactivateView,
    MovimientoListView, MovimientoCreateView,
    ProveedorListView, ProveedorCreateView, ProveedorUpdateView, ProveedorInactivateView,
    OrdenCompraListView, OrdenCompraCreateView, OrdenCompraUpdateView, OrdenCompraRecibirView, OrdenCompraCancelarView,
    ClienteListView, ClienteCreateView, ClienteUpdateView, ClienteInactivateView,
    AlmacenListView, AlmacenCreateView, AlmacenUpdateView, AlmacenInactivateView,
    CategoriaProductoListView, CategoriaProductoCreateView, CategoriaProductoUpdateView, CategoriaProductoInactivateView,
    InventarioListView,
    PedidoListView, PedidoCreateView, PedidoUpdateView, PedidoInactivateView,
    DetallePedidoUpdateView, DetallePedidoDeleteView,
    FacturaListView, FacturaCreateView, FacturaUpdateView, FacturaInactivateView, 
    MovimientoReporteView, ReporteInventarioView, ReportePedidoView, ReporteFacturaView, 
    ReporteOrdenCompraView, ReporteClienteView,
    MovimientoReporteExportView, ReporteInventarioExportView, ReportePedidoExportView, ReporteFacturaExportView, 
    ReporteOrdenCompraExportView, ReporteClienteExportView,
)

urlpatterns = [
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='bodega/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Inicio
    path('home/', home, name='home'),

    # Empleados
    path('empleados/nuevo/', crear_empleado, name='empleado_create'),
    path('empleados/', EmpleadoListView.as_view(), name='empleado_list'),
    path('empleados/editar/<int:pk>/', EmpleadoUpdateView.as_view(), name='empleado_update'),
    path('empleados/inactivar/<int:pk>/', EmpleadoInactivateView.as_view(), name='empleado_inactivate'),

    # Usuarios
    path('usuarios/', UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/nuevo/', UsuarioCreateView.as_view(), name='usuario_create'),
    path('usuarios/editar/<int:pk>/', UsuarioUpdateView.as_view(), name='usuario_update'),
    path('usuarios/inactivar/<int:pk>/', UsuarioInactivateView.as_view(), name='usuario_inactivate'),
    path('usuarios/cambiar-password/<uidb64>/<token>/', PrimerCambioPasswordView.as_view(), name='cambiar_password'),

    # Roles
    path('roles/', RolListView.as_view(), name='rol_list'),
    path('roles/nuevo/', RolCreateView.as_view(), name='rol_create'),
    path('roles/editar/<int:pk>/', RolUpdateView.as_view(), name='rol_update'),
    path('roles/inactivar/<int:pk>/', RolInactivateView.as_view(), name='rol_inactivate'),
    path('roles/permisos/<int:pk>/', RolAsignarPermisosView.as_view(), name='rol_asignar_permisos'),

    # Permisos
    path('permisos/', PermisoListView.as_view(), name='permiso_list'),
    path('permisos/nuevo/', PermisoCreateView.as_view(), name='permiso_create'),
    path('permisos/editar/<int:pk>/', PermisoUpdateView.as_view(), name='permiso_update'),
    path('permisos/inactivar/<int:pk>/', PermisoInactivateView.as_view(), name='permiso_inactivate'),

    # Productos
    path('productos/', ProductoListView.as_view(), name='producto_list'),
    path('productos/nuevo/', ProductoCreateView.as_view(), name='producto_create'),
    path('productos/editar/<int:pk>/', ProductoUpdateView.as_view(), name='producto_update'),
    path('productos/inactivar/<int:pk>/', ProductoInactivateView.as_view(), name='producto_inactivate'),
    
    # Movimientos
    path('movimientos/', MovimientoListView.as_view(), name='movimiento_list'),
    path('movimientos/nuevo/', MovimientoCreateView.as_view(), name='movimiento_create'),
    
    # Proveedores
    path('proveedores/', ProveedorListView.as_view(), name='proveedor_list'),
    path('proveedores/nuevo/', ProveedorCreateView.as_view(), name='proveedor_create'),
    path('proveedores/editar/<int:pk>/', ProveedorUpdateView.as_view(), name='proveedor_update'),
    path('proveedores/inactivar/<int:pk>/', ProveedorInactivateView.as_view(), name='proveedor_inactivate'),
    
    # Órdenes de compra
    path('ordenes-compra/', OrdenCompraListView.as_view(), name='orden_compra_list'),
    path('ordenes-compra/nueva/', OrdenCompraCreateView.as_view(), name='orden_compra_create'),
    path('ordenes-compra/editar/<int:pk>/', OrdenCompraUpdateView.as_view(), name='orden_compra_update'),
    path('ordenes-compra/recibir/<int:pk>/', OrdenCompraRecibirView.as_view(), name='orden_compra_recibir'),
    path('ordenes-compra/cancelar/<int:pk>/', OrdenCompraCancelarView.as_view(), name='orden_compra_cancelar'),
    
    # Clientes
    path('clientes/', ClienteListView.as_view(), name='cliente_list'),
    path('clientes/nuevo/', ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/editar/<int:pk>/', ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/inactivar/<int:pk>/', ClienteInactivateView.as_view(), name='cliente_inactivate'),
    
    # Almacenes
    path('almacenes/', AlmacenListView.as_view(), name='almacen_list'),
    path('almacenes/nuevo/', AlmacenCreateView.as_view(), name='almacen_create'),
    path('almacenes/editar/<int:pk>/', AlmacenUpdateView.as_view(), name='almacen_update'),
    path('almacenes/inactivar/<int:pk>/', AlmacenInactivateView.as_view(), name='almacen_inactivate'),
    
    # Categorías de Producto
    path('categorias/', CategoriaProductoListView.as_view(), name='categoria_list'),
    path('categorias/nuevo/', CategoriaProductoCreateView.as_view(), name='categoria_create'),
    path('categorias/editar/<int:pk>/', CategoriaProductoUpdateView.as_view(), name='categoria_update'),
    path('categorias/inactivar/<int:pk>/', CategoriaProductoInactivateView.as_view(), name='categoria_inactivate'),
    
    # Inventario
    path('inventario/', InventarioListView.as_view(), name='inventario_list'),
    
    # Pedidos
    path('pedidos/', PedidoListView.as_view(), name='pedido_list'),
    path('pedidos/crear/', PedidoCreateView.as_view(), name='pedido_create'),
    path('pedidos/editar/<int:pk>/', PedidoUpdateView.as_view(), name='pedido_update'),
    path('pedidos/cancelar/<int:pk>/', PedidoInactivateView.as_view(), name='pedido_inactivate'),
    
    # Detalle de Pedidos
    path('detallepedido/editar/<int:pk>/', DetallePedidoUpdateView.as_view(), name='detallepedido_update'),
    path('detallepedido/eliminar/<int:pk>/', DetallePedidoDeleteView.as_view(), name='detallepedido_delete'),
    
    # Facturas
    path('facturas/', FacturaListView.as_view(), name='factura_list'),
    path('facturas/nueva/', FacturaCreateView.as_view(), name='factura_create'),
    path('facturas/editar/<int:pk>/', FacturaUpdateView.as_view(), name='factura_update'),
    path('facturas/anular/<int:pk>/', FacturaInactivateView.as_view(), name='factura_inactivate'),
    
    # Reportes
    path('reportes/inventario/', ReporteInventarioView.as_view(), name='reporte_inventario'),
    path('reportes/inventario/exportar/', ReporteInventarioExportView.as_view(), name='exportar_inventario'),
    path('reportes/movimientos/', MovimientoReporteView.as_view(), name='reporte_movimientos'),
    path('reportes/movimientos/exportar/', MovimientoReporteExportView.as_view(), name='exportar_movimientos'),
    path('reportes/pedidos/', ReportePedidoView.as_view(), name='reporte_pedidos'),
    path('reportes/pedidos/exportar/', ReportePedidoExportView.as_view(), name='reporte_pedidos_exportar'),
    path('reportes/facturas/', ReporteFacturaView.as_view(), name='reporte_facturas'),
    path('reportes/facturas/exportar/', ReporteFacturaExportView.as_view(), name='reporte_facturas_exportar'),
    path('reportes/ordenes-compra/', ReporteOrdenCompraView.as_view(), name='reporte_ordenes_compra'),
    path('reportes/ordenes-compra/exportar/', ReporteOrdenCompraExportView.as_view(), name='reporte_ordenes_compra_exportar'),
    path('reportes/clientes/', ReporteClienteView.as_view(), name='reporte_clientes'),
    path('reportes/clientes/exportar/', ReporteClienteExportView.as_view(), name='reporte_clientes_exportar'),
]
