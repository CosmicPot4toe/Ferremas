from django.db import models
from django.contrib.auth.models import AbstractUser
#model tracker
from tracking_model import TrackingModelMixin
# Create your models here.

class User(AbstractUser):
    TIPOS_CHOICES = (
        ('Bod', 'Bodegero (Interno)'),
        ('Con', 'Contador (Interno)'),
        ('Ven', 'Vendedor (Interno)'),
        ('Cli', 'Cliente (Externo)'),
    )
    type = models.CharField(max_length=20, choices=TIPOS_CHOICES, default='Cli')

class Tienda(TrackingModelMixin,models.Model):
    id_tienda = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    comuna = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()

class Producto(TrackingModelMixin,models.Model):
    id_producto = models.AutoField(primary_key=True)
    marca = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    codigo_producto = models.CharField(max_length=50)
    descripcion = models.TextField()
    precio = models.IntegerField(default=0)
    categoria = models.ForeignKey('CategoriaProducto', on_delete=models.CASCADE)
    imagen_url = models.CharField(max_length=200) #url de la imagen

class Categoria(TrackingModelMixin,models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class CategoriaProducto(TrackingModelMixin,models.Model):
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE, null=True)
    nombre_categoria = models.CharField(max_length=100)
    subcategoria = models.CharField(max_length=100)
    sub_tipo_producto = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre_categoria

class Contacto(models.Model):
    id_contacto = models.AutoField(primary_key=True)
    tipo_contacto = models.ForeignKey('TipoContacto', on_delete=models.CASCADE)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200)

class TipoContacto(models.Model):
    id_tipo_contacto = models.AutoField(primary_key=True)

class Stock(TrackingModelMixin,models.Model):
    id = models.AutoField(primary_key=True)
    sucursal = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='stocks')
    cantidad = models.IntegerField(default=0)

class Pedido(models.Model):
    numero_pedido = models.IntegerField()
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    direccion = models.CharField(max_length=200)
    pais = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10)
    telefono = models.CharField(max_length=20)
    rut = models.CharField(max_length=14)
    metodo_envio = models.CharField(max_length=100)
    tienda_seleccionada = models.CharField(max_length=200, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.numero_pedido} - {self.nombre}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto_nombre = models.CharField(max_length=200)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.IntegerField(default=0)
    precio_total = models.IntegerField(default=0)
    imagen_url = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Detalle del Pedido #{self.pedido.numero_pedido} - {self.producto_nombre}"