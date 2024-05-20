from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms


class RegUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class DetalleEnvioForm(forms.Form):
    nombre = forms.CharField(max_length=100, label='Nombre')
    email = forms.EmailField(label='Email')
    direccion = forms.CharField(max_length=200, label='Dirección')
    pais = forms.CharField(max_length=100, label='Pais')
    ciudad = forms.CharField(max_length=100, label='Ciudad')
    region = forms.CharField(max_length=100, label='Región')
    codigo_postal = forms.CharField(max_length=10, label='Código Postal')
    telefono = forms.CharField(max_length=20, label='Teléfono')
    rut = forms.CharField(max_length=12, label='RUT')
    metodo_envio = forms.CharField(max_length=100, label='Método de Envío')
    tienda_seleccionada = forms.CharField(max_length=100, required=False, label='Tienda Seleccionada')