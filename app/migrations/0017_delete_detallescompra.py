# Generated by Django 5.0.4 on 2024-05-21 01:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_pedido_detallepedido'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DetallesCompra',
        ),
    ]