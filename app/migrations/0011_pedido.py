# Generated by Django 4.2.2 on 2024-05-20 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_delete_pedido'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_pedido', models.IntegerField()),
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
                ('tienda_seleccionada', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
    ]
