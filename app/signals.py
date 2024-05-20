#signalis xd
from django.dispatch import receiver
from django.db.models.signals import pre_save, pre_delete
from .models import Categoria, CategoriaProducto, Producto, Stock, Tienda
from .utils.apis import *

modelList=[Producto,CategoriaProducto,Categoria,Tienda,Stock]
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
		print(PhpApi(MODEL_NAME).put(update))
	else:
		insert={}
		all_fields = [f.name for f in instance._meta.fields]
		for n in all_fields:
			match n:
				case 'id_producto'|'id'|'id_tienda'|'id_categoria':
					#todavia no guardamos en la bdd asiq la id no existe
					continue
				case 'categoria'|'categoria_id'|'producto'|'sucursal':
					#tengo un foreing key dame su id
					insert[n]=getattr(instance,n).pk
					continue
			insert[n]=getattr(instance,n)
		print(PhpApi(MODEL_NAME).post(insert))

def handle_Del(sender,instance:modelTypes, **kargs):
	MODEL_NAME=instance._meta.model.__name__
	print(PhpApi(MODEL_NAME).Del(instance.pk))
	#print(MODEL_NAME,instance.pk)


for model in modelList:
	pre_save.connect(handle_pre_save,sender=model)
	pre_delete.connect(handle_Del,sender=model)
