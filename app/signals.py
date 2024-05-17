#signalis xd
from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Producto

@receiver(post_save,sender=Producto)
def handle_Product(sender, **kargs):
	print(kargs['instance'])