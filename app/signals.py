#signalis xd
from django.dispatch import receiver
from .models import Categoria, CategoriaProducto, Producto, Stock, Tienda
from .utils.apis import *
import json

modelTypes=Producto|CategoriaProducto|Categoria|Tienda|Stock

def handle_pre_save(sender,instance:modelTypes, **kargs):
	#when its an update
	MODEL_NAME=instance._meta.model.__name__
	if not instance.tracker.newly_created:
		#get the attribute that changed and save the new value on a dict
		update={"id":instance.pk}
		for k in instance.tracker.changed:
			update[k]=getattr(instance,k)
		#havent connected to the api cuz i dont ahve it on, gotta get a host lol
		PhpApi(MODEL_NAME).put(update)
	else:
		vals={}
		all_fields = [f.name for f in instance._meta.fields]
		for n in all_fields:
			match n:
				case "id_producto"|"id"|"id_tienda"|"id_categoria":
					#todavia no guardamos en la bdd asiq la id no existe
					continue
				case "categoria"|"categoria_id"|"producto"|"sucursal":
					#tengo un foreing key dame su id
					vals[n]=getattr(instance,n).pk
					continue
			vals[n]=getattr(instance,n)
		PhpApi(MODEL_NAME).post(vals)

def handle_Del(sender,instance:modelTypes, **kargs):
	MODEL_NAME=instance._meta.model.__name__
	PhpApi(MODEL_NAME).Del(instance.pk)
	#print(MODEL_NAME,instance.pk)



