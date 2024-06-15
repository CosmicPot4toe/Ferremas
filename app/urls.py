from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', index, name="index"),
    path('accounts/login/', loginP, name='login'),
	path('signup/',signup,name="signup"),
    path('logout/',logoutP,name="logout"),
    path('detalle_producto/<int:id>/', detalle_producto, name="detalle_producto"),
    path('categorias/<int:id>/', categorias, name="categorias"),
    path('buscar/', views.buscar, name='buscar'),
    path('agregar/<int:Producto_id_producto>/', agregar_producto, name="add"),
    path('eliminar/<int:Producto_id_producto>/', eliminar_producto, name="del"),
    path('restar/<int:Producto_id_producto>/', restar_producto, name="sub"),
    path('limpiar/', limpiar_carrito, name="clean"),
    path('carrito/', carrito, name='carrito'), 
    path('envio/', envio, name='envio'),
    path('api/tiendas-disponibles/', views.tiendas_disponibles, name='tiendas_disponibles'),
    path('pago/commit/', views.commit, name='commit'),
    path('revisar_pedidos/', views.revisar_pedidos, name='revisar_pedidos'),
    path('set_currency/<str:currency>/', views.set_currency, name='set_currency'),
    path('contacto/',contacto, name="contacto"),
    path('nosotros/',nosotros, name="nosotros"),
    path('add_and_checkout/<int:Producto_id_producto>/', views.add_and_checkout, name='add_and_checkout'),
    path('pedidos_pendientes/', pedidos_pendientes, name='pedidos_pendientes'),
    path('actualizar_estado_envio/<int:detalle_pedido_id>/', actualizar_estado_envio, name='actualizar_estado_envio'),

    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/create_user/', create_user, name='create_user'),
    path('update_user/<int:user_id>/', update_user, name='update_user'),
    path('admin/delete_user/<int:user_id>/', delete_user, name='delete_user'),
    
    path('admin/create_producto/', create_producto, name='create_producto'),
    path('admin/update_producto/<int:producto_id>/', update_producto, name='update_producto'),
    path('admin/delete_producto/<int:producto_id>/', delete_producto, name='delete_producto'),

    path('admin/create_tienda/', create_tienda, name='create_tienda'),
    path('admin/update_tienda/<int:tienda_id>/', update_tienda, name='update_tienda'),
    path('admin/delete_tienda/<int:tienda_id>/', delete_tienda, name='delete_tienda'),

    path('admin/create_categoria/', create_categoria, name='create_categoria'),
    path('admin/update_categoria/<int:categoria_id>/', update_categoria, name='update_categoria'),
    path('admin/delete_categoria/<int:categoria_id>/', delete_categoria, name='delete_categoria'),

    path('admin/create_stock/', create_stock, name='create_stock'),
    path('admin/update_stock/<int:stock_id>/', update_stock, name='update_stock'),
    path('admin/delete_stock/<int:stock_id>/', delete_stock, name='delete_stock'),
]
