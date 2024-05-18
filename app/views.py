from django.http import HttpRequest, HttpResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages as msgs
from .forms import *
from .models import *
from app.carrito import Carrito
from django.template.defaultfilters import floatformat

def buscar(request):
    query = request.GET.get('q')
    if query:
        resultados = Producto.objects.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(marca__icontains=query) |
            Q(categoria__nombre_categoria__icontains=query) |
            Q(categoria__subcategoria__icontains=query) |
            Q(categoria__sub_tipo_producto__icontains=query)
        ).distinct()
    else:
        resultados = Producto.objects.none()

    return render(request, 'app/buscar.html', {'resultados': resultados, 'query': query})


def index(request):
    # Obtener los últimos 5 productos añadidos, ordenados por id_producto descendente
    productos = Producto.objects.order_by('-id_producto')[:5]
    return render(request, 'app/index.html', {'producto': productos})

def detalle_producto(request, id):
    # Obtener el producto por su ID
    producto = get_object_or_404(Producto, id_producto=id)

    # Obtener la categoría asociada al producto
    categoria_producto = producto.categoria
    categoria = categoria_producto.categoria

    # Obtener todos los stocks para el producto
    stocks = Stock.objects.filter(producto=producto)

    # Crear un diccionario para almacenar el stock por tienda
    stocks_por_tienda = {}
    for stock in stocks:
        tienda = stock.sucursal.nombre
        cantidad = stock.cantidad
        if tienda in stocks_por_tienda:
            stocks_por_tienda[tienda] += cantidad
        else:
            stocks_por_tienda[tienda] = cantidad

    # Preparar los datos a enviar al template
    data = {
        'producto': producto,
        'id_categoria': categoria.id_categoria,
        'nombre_categoria': categoria.nombre,
        'stocks_por_tienda': stocks_por_tienda,
    }

    # Renderizar el template con los datos
    return render(request, 'app/detalle_producto.html', data)

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

def signup(request):
    if request.method == 'POST':
        form = RegUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.type = 'Cli'  # Asignar el valor predeterminado para type
            user.save()
            username = form.cleaned_data.get('username')
            msgs.success(request, f'Cuenta creada exitosamente para {username}. ¡Ahora puedes iniciar sesión!')
            return redirect('login')
    else:
        form = RegUserForm()
    
    return render(request, 'registration/registro.html', {'form': form})

def logoutP(req: HttpRequest):
	logout(req)
	return redirect('index')


#VISTAS PARA EL CARRITO
def agregar_producto(request, Producto_id_producto):
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))  # Obtener la cantidad del formulario POST
        carrito = Carrito(request)
        producto = Producto.objects.get(id_producto=Producto_id_producto)
        carrito.agregar(producto, cantidad=cantidad)  # Pasar la cantidad al método agregar
        return redirect('carrito')
    else:
        # Manejar el caso en que no se reciba una solicitud POST
        # Por ejemplo, redirigir o mostrar un mensaje de error
        return HttpResponse("Método no permitido")

def eliminar_producto(request, Producto_id_producto):
    carrito = Carrito(request)
    producto = Producto.objects.get(id_producto=Producto_id_producto)
    carrito.eliminar(producto)
    return redirect("carrito")

def restar_producto(request, Producto_id_producto):
    carrito = Carrito(request)
    producto = Producto.objects.get(id_producto=Producto_id_producto)
    carrito.restar(producto)
    return redirect("carrito")

def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return redirect("carrito.html")

def carrito(request):
    carrito_dict = request.session.get("carrito", {})
    total_carrito = 0
    neto_formateado = 0
    iva_formateado = 0 

    for key, value in carrito_dict.items():
        # Obtener el precio base del producto desde la base de datos
        producto = Producto.objects.get(id_producto=value["id"])
        value["precio_base"] = producto.precio
        # Calcular el precio total por producto
        value["precio_total"] = producto.precio * value["cantidad"]
        # Sumar al total del carrito
        value["imagen_url"] = producto.imagen_url

        value["marca"] = producto.marca
        total_carrito += value["precio_total"]

        # Calcular el IVA y el precio total del carrito
        iva = total_carrito * 0.19
        neto = total_carrito * 0.81
        neto_formateado = floatformat(neto, 0)  # Formatear neto con dos decimales
        iva_formateado = floatformat(iva,0)


    context = {
        "carrito_dict": carrito_dict,
        "total_carrito": total_carrito,
        "neto": neto_formateado,
        "iva": iva_formateado,
    }

    return render(request, 'app/carrito.html', context)