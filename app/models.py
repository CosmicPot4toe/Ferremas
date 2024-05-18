from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
		TIPOS_CHOICES = (
				('Bod', 'Bodegero (Interno)'),
				('Con', 'Contador (Interno)'),
				('Ven', 'Vendedor (Interno)'),
				('Cli', 'Cliente (Externo)'),
		)
		type = models.CharField(max_length=20, choices=TIPOS_CHOICES, default='Cli')
		# rol = models.ForeignKey('Rol', on_delete=models.CASCADE)

from django.db import models

class Tienda(models.Model):
		id_tienda = models.AutoField(primary_key=True)
		nombre = models.CharField(max_length=100)
		direccion = models.CharField(max_length=200)
		comuna = models.CharField(max_length=100)
		region = models.CharField(max_length=100)
		telefono = models.CharField(max_length=20)
		email = models.EmailField()

class ResponsabilidadTienda(models.Model):
		tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
		empleado = models.ForeignKey('Empleado', on_delete=models.CASCADE)

class Empleado(models.Model):
		id_empleado = models.AutoField(primary_key=True)
		nombre = models.CharField(max_length=100)
		apellido = models.CharField(max_length=100)
		tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
		usuario = models.ForeignKey('User', on_delete=models.CASCADE)

class Producto(models.Model):
		id_producto = models.AutoField(primary_key=True)
		marca = models.CharField(max_length=100)
		nombre = models.CharField(max_length=100)
		codigo_producto = models.CharField(max_length=50)
		descripcion = models.TextField()
		precio = models.IntegerField(default=0)
		categoria = models.ForeignKey('CategoriaProducto', on_delete=models.CASCADE)
		imagen_url = models.CharField(max_length=200) #url de la imagen
		def __str__(self):
				return self.nombre

class Categoria(models.Model):
		id_categoria = models.AutoField(primary_key=True)
		nombre = models.CharField(max_length=100)

		def __str__(self):
				return self.nombre

class CategoriaProducto(models.Model):
		categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, null=True)
		nombre_categoria = models.CharField(max_length=100)
		subcategoria = models.CharField(max_length=100)
		sub_tipo_producto = models.CharField(max_length=100)
		def __str__(self):
				return self.nombre_categoria


class Cliente(models.Model):
		id_cliente = models.AutoField(primary_key=True)
		nombre = models.CharField(max_length=100)
		apellido = models.CharField(max_length=100)
		usuario = models.ForeignKey('User', on_delete=models.CASCADE)

class Contacto(models.Model):
		id_contacto = models.AutoField(primary_key=True)
		tipo_contacto = models.ForeignKey('TipoContacto', on_delete=models.CASCADE)
		email = models.EmailField()
		telefono = models.CharField(max_length=20)
		direccion = models.CharField(max_length=200)

class TipoContacto(models.Model):
		id_tipo_contacto = models.AutoField(primary_key=True)
		tipo = models.CharField(max_length=50)

class Pedido(models.Model):
		id_pedido = models.AutoField(primary_key=True)
		cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
		fecha = models.DateField()
		total = models.DecimalField(max_digits=10, decimal_places=2)
		ESTADOS = (
				('Pendiente', 'Pendiente'),
				('Aprobado', 'Aprobado'),
				('Enviado', 'Enviado'),
				('Entregado', 'Entregado'),
		)
		estado = models.CharField(max_length=20, choices=ESTADOS)

class DetallePedido(models.Model):
		id_detalle = models.AutoField(primary_key=True)
		pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
		producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
		cantidad = models.IntegerField()
		precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

class Pago(models.Model):
		id_pago = models.AutoField(primary_key=True)
		pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
		metodo_pago = models.ForeignKey('MetodoPago', on_delete=models.CASCADE)
		monto = models.DecimalField(max_digits=10, decimal_places=2)
		fecha = models.DateField()

class MetodoPago(models.Model):
		id_metodo_pago = models.AutoField(primary_key=True)
		metodo = models.CharField(max_length=50)


# te volviste redundante, podemos usar el usuario q creamos anteriormente para el tipo
# class Usuario(models.Model):
# 		id_usuario = models.AutoField(primary_key=True)
# 		nombre_usuario = models.CharField(max_length=100)
# 		contraseña = models.CharField(max_length=200)  # La contraseña podría ser encriptada mediante alguna función hash.
# 		email = models.EmailField()
# 		rol = models.ForeignKey('Rol', on_delete=models.CASCADE)

# class Rol(models.Model):
# 		id_rol = models.AutoField(primary_key=True)
# 		tipo_rol = models.CharField(max_length=50)

class Stock(models.Model):
		id = models.AutoField(primary_key=True)
		sucursal = models.ForeignKey(Tienda, on_delete=models.CASCADE)
		producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='stocks')
		cantidad = models.IntegerField(default=0)

class Carrito(models.Model):
		id = models.AutoField(primary_key=True)
		cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
		fecha_creacion = models.DateTimeField(auto_now_add=True)
		productos = models.ManyToManyField(Producto, through='ElementoCarrito')

class ElementoCarrito(models.Model):
		carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
		producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
		cantidad = models.IntegerField(default=1)