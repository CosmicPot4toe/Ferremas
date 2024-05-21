from django.apps import AppConfig
from django.db.models.signals import pre_save, pre_delete

class AppConfig(AppConfig):
		default_auto_field = 'django.db.models.BigAutoField'
		name = 'app'
		def ready(self):
				# Implicitly connect signal handlers decorated with @receiver.
				from .signals import handle_pre_save,handle_Del
				from .models import Categoria, CategoriaProducto, Producto, Stock, Tienda
				
				modelList=[Producto,CategoriaProducto,Categoria,Tienda,Stock]
				for model in modelList:
					pre_save.connect(handle_pre_save,sender=model)
					pre_delete.connect(handle_Del,sender=model)
