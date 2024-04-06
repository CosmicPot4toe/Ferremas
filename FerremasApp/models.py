from django.db import models

# Create your models here.
class Tipo_Us(models.Model):
	nombre= models.CharField(max_length=20)
	def __str__(slf):
		return str(slf.nombre)

class Usuario(models.Model):
	nombre = models.CharField(max_length=45)
	correo = models.EmailField()
	tipo = models.ForeignKey(Tipo_Us,on_delete=models.CASCADE)