from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    TIPOS_CHOICES = (
        ('Bod', 'Bodegero (Interno)'),
        ('Con', 'Contador (Interno)'),
        ('Ven', 'Vendedor (Interno)'),
        ('Cli', 'Cliente (Externo)'),
    )
    type = models.CharField(max_length=20, choices=TIPOS_CHOICES, default='Cli')