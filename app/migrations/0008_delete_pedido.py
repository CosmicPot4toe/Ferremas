# Generated by Django 4.2.2 on 2024-05-19 07:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_remove_pedido_metodo_envio'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Pedido',
        ),
    ]