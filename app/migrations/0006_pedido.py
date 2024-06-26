# Generated by Django 4.2.2 on 2024-05-19 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_remove_pago_metodo_pago_remove_pago_pedido_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('direccion', models.CharField(max_length=200)),
                ('pais', models.CharField(max_length=100)),
                ('ciudad', models.CharField(max_length=100)),
                ('region', models.CharField(max_length=100)),
                ('codigo_postal', models.CharField(max_length=10)),
                ('telefono', models.CharField(max_length=20)),
                ('rut', models.CharField(max_length=14)),
                ('metodo_envio', models.CharField(max_length=100)),
            ],
        ),
    ]
