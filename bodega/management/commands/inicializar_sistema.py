from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from bodega.models import Permiso, Rol, Empleado, Usuario

class Command(BaseCommand):
    help = 'Inicializa permisos, roles, empleado y usuario admin para el sistema de gestión de bodega'

    def handle(self, *args, **kwargs):
        permisos = [
            'ver_empleado', 'crear_empleado', 'editar_empleado', 'inactivar_empleado',
            'ver_usuario', 'crear_usuario', 'editar_usuario', 'inactivar_usuario',
            'ver_rol', 'crear_rol', 'editar_rol', 'inactivar_rol',
            'ver_permiso', 'crear_permiso', 'editar_permiso', 'inactivar_permiso',
            'ver_reporte_inventario', 'ver_reporte_compras', 'ver_reporte_ventas',
            'ver_producto', 'crear_producto', 'editar_producto', 'inactivar_producto',
            'ver_orden_compra', 'crear_orden_compra', 'ver_orden_venta', 'crear_orden_venta',
            'ver_dashboard'
        ]

        permisos_creados = []
        for nombre in permisos:
            permiso, _ = Permiso.objects.get_or_create(nombre=nombre, descripcion=nombre.capitalize(), activo=True)
            permisos_creados.append(permiso)

        rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador', descripcion='Acceso total', activo=True)
        rol_encargado, _ = Rol.objects.get_or_create(nombre='Encargado', descripcion='Acceso parcial', activo=True)
        rol_vendedor, _ = Rol.objects.get_or_create(nombre='Vendedor', descripcion='Acceso a ventas', activo=True)

        rol_admin.permisos.set(permisos_creados)
        rol_admin.save()

        empleado_admin, _ = Empleado.objects.get_or_create(
            nombre='Admin',
            apellido='Principal',
            direccion='Calle Principal',
            telefono='0981123456',
            email='bodegaeirete@gmail.com',
            fecha_contratacion=now().date(),
            cargo=rol_admin,
            activo=True
        )

        admin_user, created = Usuario.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'bodegaeirete@gmail.com',
                'estado': 'activo',
                'empleado': empleado_admin,
                'rol': rol_admin,
                'is_superuser': True,
                'is_staff': True,
                'password': make_password('admin1234')
            }
        )

        if not created:
            self.stdout.write(self.style.WARNING('⚠️ El usuario "admin" ya existía.'))

        self.stdout.write(self.style.SUCCESS('✅ Sistema inicializado correctamente: permisos, roles, empleado y usuario admin.'))
