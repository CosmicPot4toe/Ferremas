from django.http import HttpRequest
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages as msgs
from .forms import *
from .models import *
#from .apis import *

# Create your views here.

def index(request):
    # Obtener los últimos 5 productos añadidos, ordenados por id_producto descendente
    productos = Producto.objects.order_by('-id_producto')[:5]
    return render(request, 'app/index.html', {'producto': productos})

def detalle_producto(request, id):
    # Obtener el producto por su ID
    producto = get_object_or_404(Producto, id_producto=id)

    # Pasar el producto como contexto al template
    return render(request, 'app/detalle_producto.html', {'producto': producto})

def categorias(request, id):
    # Obtener la categoría correspondiente al ID
    categoria = Categoria.objects.get(id_categoria=id)

    # Filtrar los productos por el ID de la categoría
    producto = Producto.objects.filter(categoria_id=id)

    return render(request, 'app/categorias.html', {'categoria': categoria, 'producto': producto})


def loginP(req: HttpRequest):
    if req.method == 'POST':
        usern_or_email = req.POST.get('username_or_email')
        passw = req.POST.get('password')

        print("Username or email:", usern_or_email)  # Mensaje de depuración
        print("Password:", passw)  # Mensaje de depuración

        if usern_or_email is not None and passw is not None:
            # Buscar si el usuario existe con el nombre de usuario o correo electrónico
            user = None
            if '@' in usern_or_email:
                try:
                    user = User.objects.get(email=usern_or_email)
                except User.DoesNotExist:
                    pass
            else:
                user = authenticate(req, username=usern_or_email, password=passw)

            if user is not None:
                print("Usuario autenticado:", user.username)  # Mensaje de depuración
                login(req, user)
                return redirect('index')
            else:
                print("Usuario no autenticado")  # Mensaje de depuración
                msgs.info(req, 'Nombre de usuario, correo electrónico o contraseña incorrectos')
        else:
            print("Nombre de usuario o contraseña no proporcionados")  # Mensaje de depuración
            msgs.info(req, 'Nombre de usuario o contraseña no proporcionados')
            
    return render(req, 'registration/login.html')

"""
def signup(req: HttpRequest):
	form = RegUserForm()
	if req.POST:
		form = RegUserForm(req.POST)
		if form.is_valid():
			form.save()
			name =form.cleaned_data.get('username')
			msgs.success(req,'Cuenta creada con exito '+ name)
			return redirect('login')
	ctx={'form':form}
	return render(req,'registration/registro.html',ctx)

    """
def signup(req):
    if req.method == 'POST':
        form = RegUserForm(req.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            msgs.success(req, f'Cuenta creada exitosamente para {username}. ¡Ahora puedes iniciar sesión!')
            return redirect('login')

            # Definir las variables para mostrar Sweet Alert
            show_sweetalert = True
            sweetalert_title = "Registro Exitoso"
            sweetalert_message = f"Cuenta creada exitosamente para {username}. ¡Ahora puedes iniciar sesión!"
            sweetalert_icon = "success"

            return render(req, 'registration/registro.html', {
                'show_sweetalert': show_sweetalert,
                'sweetalert_title': sweetalert_title,
                'sweetalert_message': sweetalert_message,
                'sweetalert_icon': sweetalert_icon,
            })
    else:
        form = RegUserForm()
    
    return render(req, 'registration/registro.html', {'form': form})

def logoutP(req: HttpRequest):
	logout(req)
	return redirect('index')