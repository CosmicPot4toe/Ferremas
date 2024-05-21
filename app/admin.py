from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BUA
from .models import *

# Register your models here.

class UserAdmin(BUA):
    fieldsets = BUA.fieldsets+ (
        (                      
            'Type', # you can also use None 
            {
                'fields': (
                    'type',
                ),
            },
        ),
    )

admin.site.register(User,UserAdmin)
admin.site.register(Tienda)
admin.site.register(Producto)
admin.site.register(CategoriaProducto)
admin.site.register(Categoria)
admin.site.register(Contacto)
admin.site.register(TipoContacto)
admin.site.register(Stock)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
