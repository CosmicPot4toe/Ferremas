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

]
