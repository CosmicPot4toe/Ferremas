#signalis xd
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete
from .models import Producto
from .utils.apis import *
#	here you can update, insert and delete
#	sadly thats the only thing you can do here with the api
#	if you want to get something you'll've to make another
#	api object and get things from that
@receiver(pre_save,sender=Producto)
def handle_Product(sender,instance:Producto, **kargs):
	#when its an update
	if not instance.tracker.newly_created:
		#get the attribute that changed and save the new value on a dict
		update={"id":instance.pk}
		for k in instance.tracker.changed:
			update[k]=getattr(instance,k)
		#havent connected to the api cuz i dont ahve it on, gotta get a host lol
		PhpApi('Producto').put(update)

@receiver(post_delete,sender=Producto)
def handleProductDel(sender,instance:Producto, **kargs):
	print(PhpApi('Producto').Del(instance.pk))# to delete shit