# Generated by Django 4.2.2 on 2024-05-20 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_alter_detallepedido_precio_total_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='detallepedido',
            name='imagen_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]