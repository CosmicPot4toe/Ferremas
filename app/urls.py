from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name="index"),
    path('login/',loginP,name="login"),
	path('signup/',signup,name="signup"),
    path('logout/',logoutP,name="logout"),
    path('detalle_producto/<int:id>/', detalle_producto, name="detalle_producto"),
    path('categorias/<int:id>/', categorias, name="categorias"),
]
