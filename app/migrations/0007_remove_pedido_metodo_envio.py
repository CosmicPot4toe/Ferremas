# Generated by Django 4.2.2 on 2024-05-19 07:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_pedido'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedido',
            name='metodo_envio',
        ),
    ]
