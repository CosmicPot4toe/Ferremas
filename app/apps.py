from django.apps import AppConfig
from django.db.models.signals import post_save, pre_delete

class AppConfig(AppConfig):
		default_auto_field = 'django.db.models.BigAutoField'
		name = 'app'
		def ready(self):
				# Implicitly connect signal handlers decorated with @receiver.
				from .signals import handle_post_save,handle_Del
				from .models import Categoria, CategoriaProducto, Producto, Stock, Tienda
				
				modelList=[Producto,CategoriaProducto,Categoria,Tienda,Stock]
				for model in modelList:
					post_save.connect(handle_post_save,sender=model)
					pre_delete.connect(handle_Del,sender=model)
