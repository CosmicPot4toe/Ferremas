# Generated by Django 4.2.2 on 2024-05-20 04:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_detallepedido_imagen_url'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DetallePedido',
        ),
        migrations.DeleteModel(
            name='Pedido',
        ),
    ]
