# Generated by Django 4.2.2 on 2024-06-19 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_user_ciudad_user_codigo_postal_user_direccion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='pais_abreviado',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
