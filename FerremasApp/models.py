from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
	tipos={
		"Internos":{
			"Bod":"Bodegero",
			"Con":"Contador"
		},
		"Externos":{
			"Cli":"Cliente"
		}
	}
	type = models.CharField(max_length=20,choices=tipos)