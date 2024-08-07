from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django import forms


class RegUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class DetalleEnvioForm(forms.Form):
    nombre = forms.CharField(max_length=100, label='Nombre')
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'example@example.com'}))
    direccion = forms.CharField(max_length=200, label='Dirección',)
    pais = forms.CharField(max_length=100, label='Pais', widget=forms.Select(attrs={'class': 'crs-country', 'data-region-id': 'region', 'data-default-option': 'Seleccionar país'}))
    ciudad = forms.CharField(max_length=100, label='Ciudad')
    region = forms.CharField(max_length=100, label='Región')
    codigo_postal = forms.CharField(max_length=10, label='Código Postal')
    telefono = forms.CharField(max_length=20, label='Teléfono', widget=forms.TextInput(attrs={'id': 'phone'}))
    rut = forms.CharField(max_length=12, label='RUT')
    metodo_envio = forms.CharField(max_length=100, label='Método de Envío')
    tienda_seleccionada = forms.CharField(max_length=100, required=False, label='Tienda Seleccionada')


class ContactoFrom (forms.ModelForm):
    #nombre = forms.CharField(widget=forms.TextInput(attrs={"class":"form-control"}))
    class Meta:
        model = Contacto
        #fields = ["nombre","correo","tipo_consulta","mensaje","avisos"] para dar el orden que uno quiera
        fields = '__all__'
######

class ActualizarEstadoEnvioForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['estado_envio']
        widgets = {
            'estado_envio': forms.Select(choices=[
                ('Enviado', 'Enviado'),
                ('En Sucursal', 'En Sucursal'),
            ])
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'type']

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'

class TiendaForm(forms.ModelForm):
    class Meta:
        model = Tienda
        fields = '__all__'

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = '__all__'

class CategoriaProdForm(forms.ModelForm):
    class Meta:
        model = CategoriaProducto
        fields = '__all__'

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['sucursal', 'producto', 'cantidad']