from datetime import datetime, timezone
from datetime import datetime
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages as msgs
from django.urls import reverse
from flask import render_template, request
from django.db.models import Sum
from app.context_processor import total_carrito
from .utils.apis import Mindicador, PhpApi
from .forms import *
from .models import *
from app.carrito import Carrito
from django.template.defaultfilters import floatformat
import random
from django.shortcuts import render, redirect
from django.http import HttpRequest
from transbank.webpay.webpay_plus.transaction import Transaction
from django.contrib.humanize.templatetags.humanize import intcomma


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

    mindicador = Mindicador('dolar')
    dollar_value = mindicador.get_dollar_value_today()
    currency = request.session.get('currency', 'CLP')
    for producto in resultados:
        if currency == 'USD' and dollar_value:
            producto.precio = producto.precio / dollar_value


    return render(request, 'app/buscar.html', {'resultados': resultados, 'query': query, 'currency':currency})


def index(request):
    # Obtener los últimos 5 productos añadidos, ordenados por id_producto descendente
    productos = Producto.objects.all().order_by('-id_producto')[:5]
    #productos = PhpApi('Producto').getAll()[-5:]
    mindicador = Mindicador('dolar')
    dollar_value = mindicador.get_dollar_value_today()
    currency = request.session.get('currency', 'CLP')
    for producto in productos:
        if currency == 'USD' and dollar_value:
            producto.precio = producto.precio / dollar_value

    data ={
        'productos': productos,
        'currency': currency,
        'dollar_value':dollar_value
    }
    return render(request, 'app/index.html', data)

def detalle_producto(request, id):
    # Obtener el producto por su ID
    producto = get_object_or_404(Producto, id_producto=id)

    # Obtener el valor del dólar de hoy
    mindicador = Mindicador('dolar')
    dollar_value = mindicador.get_dollar_value_today()

    # Obtener la divisa seleccionada de la sesión
    currency = request.session.get('currency', 'CLP')

    # Ajustar el precio del producto según la divisa seleccionada
    if currency == 'USD' and dollar_value:
        producto.precio = producto.precio / dollar_value

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
        'currency': currency,
    }

    # Renderizar el template con los datos
    return render(request, 'app/detalle_producto.html', data)

def categorias(request, id):
    # Obtener la categoría correspondiente al ID
    categoria = get_object_or_404(Categoria, id_categoria=id)

    # Filtrar los productos por el ID de la categoría
    productos = Producto.objects.filter(categoria_id=id)

    # Obtener el valor del dólar de hoy
    mindicador = Mindicador('dolar')
    dollar_value = mindicador.get_dollar_value_today()

    # Obtener la divisa seleccionada de la sesión
    currency = request.session.get('currency', 'CLP')

    # Ajustar el precio de cada producto según la divisa seleccionada
    for producto in productos:
        if currency == 'USD' and dollar_value:
            producto.precio = producto.precio / dollar_value

    return render(request, 'app/categorias.html', {'categoria': categoria, 'productos': productos, 'currency': currency})


def loginP(req: HttpRequest):
    if req.method == 'POST':
        usern_or_email = req.POST.get('username_or_email')
        passw = req.POST.get('password')
        next_url = req.POST.get('next', 'index')

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
                return redirect(next_url)
            else:
                print("Usuario no autenticado")  # Mensaje de depuración
                msgs.info(req, 'Nombre de usuario, correo electrónico o contraseña incorrectos')
        else:
            print("Nombre de usuario o contraseña no proporcionados")  # Mensaje de depuración
            msgs.info(req, 'Nombre de usuario o contraseña no proporcionados')

    else:
        next_url = req.GET.get('next', 'index')

    return render(req, 'registration/login.html', {'next': next_url})

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
    carrito = Carrito(request)
    total_carrito = 0
    cantidad_productos = carrito.obtener_cantidad_productos()

    # Obtener el valor del dólar de hoy
    mindicador = Mindicador('dolar')
    dollar_value = mindicador.get_dollar_value_today()

    # Obtener la divisa seleccionada de la sesión
    currency = request.session.get('currency', 'CLP')

    for key, value in carrito_dict.items():
        # Obtener el precio base del producto desde la base de datos
        producto = Producto.objects.get(id_producto=value["id"])
        value["precio_base"] = producto.precio

        # Calcular el precio total por producto
        value["precio_total"] = producto.precio * value["cantidad"]

        # Ajustar los precios según la divisa seleccionada
        if currency == 'USD' and dollar_value:
            value["precio_base"] = value["precio_base"] / dollar_value
            value["precio_total"] = value["precio_total"] / dollar_value

        # Sumar al total del carrito
        value["imagen_url"] = producto.imagen_url
        value["marca"] = producto.marca
        total_carrito += value["precio_total"]

    context = {
        "carrito_dict": carrito_dict,
        "total_carrito": total_carrito,
        "cantidad_productos": cantidad_productos,
        "currency": currency,
    }

    if currency == 'CLP':
        iva = total_carrito * 0.19
        neto = total_carrito * 0.81
        context["neto"] = floatformat(neto, 0)  # Formatear neto con dos decimales
        context["iva"] = floatformat(iva, 0)  # Formatear IVA con dos decimales

    return render(request, 'app/carrito.html', context)

def tiendas_disponibles(request):
    carrito_dict = request.session.get("carrito", {})
    productos_ids = [value["id"] for value in carrito_dict.values()]
    
    tiendas_disponibles = Tienda.objects.filter(stock__producto__id_producto__in=productos_ids, stock__cantidad__gt=0).distinct()
    
    tiendas_list = []
    for tienda in tiendas_disponibles:
        tiene_todos_productos = True
        for producto_id in productos_ids:
            if not Stock.objects.filter(sucursal=tienda, producto_id=producto_id, cantidad__gt=0).exists():
                tiene_todos_productos = False
                break
        if tiene_todos_productos:
            tiendas_list.append({'id': tienda.id_tienda, 'nombre': tienda.nombre, 'direccion': tienda.direccion})

    return JsonResponse({'tiendas': tiendas_list})


    token = request.GET.get("token_ws")
    response = Transaction().commit(token=token)
    
    total_carrito_value = total_carrito(request)
    if isinstance(total_carrito_value, dict):
        total_carrito_value = total_carrito_value.get('total_carrito', 0)
    
    carrito_dict = request.session.get("carrito", {})
    numero_pedido = request.session.get('buy_order')
    pedido = Pedido.objects.get(numero_pedido=numero_pedido)
    transaction_date = datetime.strptime(response['transaction_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
    
    currency = request.session.get('currency', 'CLP')
    mindicador = Mindicador('dolar')
    dollar_value = mindicador.get_dollar_value_today()

    # Realizar copia de carrito_dict para manipulación de precios sin afectar el carrito original
    carrito_dict_converted = carrito_dict.copy()

    # Ajustar los precios según la divisa seleccionada solo para la vista
    for key, item in carrito_dict_converted.items():
        if currency == 'USD' and dollar_value:
            item['precio_base'] = item['precio_base'] / dollar_value
            item['precio_total'] = item['precio_total'] / dollar_value

    if currency == 'USD' and dollar_value:
        total_carrito_value = total_carrito_value / dollar_value

    return render(request, 'app/pago.html', {
        'response': response,
        'carrito_dict': carrito_dict_converted,
        'total_carrito': total_carrito_value,
        'currency': currency,
        'pedido': pedido,
        'transaction_date': transaction_date
    })


def commit(request):
    token = request.GET.get("token_ws")
    response = Transaction().commit(token=token)
    
    carrito_dict = request.session.get("carrito", {})
    numero_pedido = request.session.get('buy_order')
    pedido = Pedido.objects.get(numero_pedido=numero_pedido)
    transaction_date = datetime.strptime(response['transaction_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
    
    currency = request.session.get('currency', 'CLP')
    mindicador = Mindicador('dolar')
    dollar_value = mindicador.get_dollar_value_today()

    # Rescatar los detalles del pedido guardados en CLP
    detalles_pedido = DetallePedido.objects.filter(pedido=pedido)
    detalles_pedido_dict = []
    total_carrito_value = 0  # Inicializar el total del carrito

    for detalle in detalles_pedido:
        producto_id = detalle.producto_nombre
        carrito_item = next((item for key, item in carrito_dict.items() if item.get('nombre') == producto_id), None)
        imagen_url = carrito_item['imagen_url'] if carrito_item else ''

        detalle_dict = {
            'producto_nombre': detalle.producto_nombre,
            'cantidad': detalle.cantidad,
            'precio_unitario': detalle.precio_unitario,
            'precio_total': detalle.precio_total,
            'imagen_url': imagen_url,
        }
        total_carrito_value += detalle.precio_total  # Calcular el total del carrito en CLP

        # Ajustar los precios según la divisa seleccionada solo para la visualización
        if currency == 'USD' and dollar_value:
            detalle_dict['precio_unitario'] = detalle.precio_unitario / dollar_value
            detalle_dict['precio_total'] = detalle.precio_total / dollar_value
        
        detalles_pedido_dict.append(detalle_dict)

    # Ajustar el total del carrito según la divisa seleccionada solo para la visualización
    if currency == 'USD' and dollar_value:
        total_carrito_value = total_carrito_value / dollar_value

    # Formatear el total del carrito para la visualización
    if currency == 'USD':
        total_carrito_formatted = f'${total_carrito_value:,.2f} USD'
    else:
        total_carrito_formatted = f'${intcomma(int(total_carrito_value))} CLP'

    request.session.pop('carrito', None)
    request.session.pop('envio_datos', None)

    return render(request, 'app/pago.html', {
        'response': response,
        'carrito_dict': detalles_pedido_dict,  # Usar los detalles del pedido convertidos
        'total_carrito': total_carrito_formatted,
        'currency': currency,
        'pedido': pedido,
        'transaction_date': transaction_date
    })

def envio(request: HttpRequest):
    carrito_dict = request.session.get("carrito", {})
    total_carrito = 0

    # Obtener el valor del dólar de hoy
    mindicador = Mindicador('dolar')
    dollar_value = mindicador.get_dollar_value_today()

    # Obtener la divisa seleccionada de la sesión
    currency = request.session.get('currency', 'CLP')

    for key, value in carrito_dict.items():
        producto = Producto.objects.get(id_producto=value["id"])
        value["precio_base"] = producto.precio
        value["precio_total"] = producto.precio * value["cantidad"]

        # Ajustar los precios según la divisa seleccionada
        if currency == 'USD' and dollar_value:
            value["precio_base"] = value["precio_base"] / dollar_value
            value["precio_total"] = value["precio_total"] / dollar_value

        value["precio_base_formatted"] = floatformat(value["precio_base"], 2) if currency == 'USD' else intcomma(value["precio_base"])
        value["precio_total_formatted"] = floatformat(value["precio_total"], 2) if currency == 'USD' else intcomma(value["precio_total"])

        value["imagen_url"] = producto.imagen_url
        value["marca"] = producto.marca
        total_carrito += value["precio_total"]

    # Calcular IVA y Neto en CLP
    total_carrito_clp = total_carrito if currency == 'CLP' else total_carrito * dollar_value

    iva = total_carrito_clp * 0.19
    neto = total_carrito_clp * 0.81

    if request.method == 'POST':
        form = DetalleEnvioForm(request.POST)
        if form.is_valid():
            envio_datos = form.cleaned_data
            request.session['envio_datos'] = envio_datos

            metodo_envio = 'envio-internacional' if envio_datos['pais'] != 'Chile' else request.POST.get('metodo_envio', '')
            tienda_seleccionada_id = request.POST.get('tienda_select', '')

            if metodo_envio == 'retiro-tienda' and tienda_seleccionada_id:
                tienda_seleccionada = Tienda.objects.get(id_tienda=tienda_seleccionada_id).nombre
            else:
                tienda_seleccionada = ''

            buy_order = str(random.randrange(1000000, 99999999))
            session_id = str(random.randrange(1000000, 99999999))
            return_url = request.build_absolute_uri(reverse('commit'))

            # Crear transacción con el total en CLP
            response = Transaction().create(buy_order, session_id, int(total_carrito_clp), return_url)

            request.session['webpay_response'] = response
            request.session['buy_order'] = buy_order
            request.session['session_id'] = session_id

            pedido = Pedido(
                numero_pedido=buy_order,
                nombre=envio_datos['nombre'],
                email=envio_datos['email'],
                direccion=envio_datos['direccion'],
                pais=envio_datos['pais'],
                ciudad=envio_datos['ciudad'],
                region=envio_datos['region'],
                codigo_postal=envio_datos['codigo_postal'],
                telefono=envio_datos['telefono'],
                rut=envio_datos['rut'],
                metodo_envio=metodo_envio,
                tienda_seleccionada=tienda_seleccionada
            )
            pedido.save()

            for key, value in carrito_dict.items():
                detalle_pedido = DetallePedido(
                    pedido=pedido,
                    producto_nombre=value["nombre"],
                    cantidad=value["cantidad"],
                    precio_unitario=producto.precio,  # Guardar siempre en CLP
                    precio_total=producto.precio * value["cantidad"],  # Guardar siempre en CLP
                    imagen_url=value["imagen_url"]
                )
                detalle_pedido.save()

            return redirect(response['url'] + '?token_ws=' + response['token'])
    else:
        form = DetalleEnvioForm(initial=request.session.get('envio_datos', {}))

    productos_ids = [value["id"] for value in carrito_dict.values()]

    tiendas_disponibles = Tienda.objects.filter(
        id_tienda__in=Stock.objects.filter(
            producto_id__in=productos_ids, cantidad__gt=0
        ).values_list('sucursal_id', flat=True).distinct()
    )

    tiendas_validas = []
    for tienda in tiendas_disponibles:
        tiene_todos_productos = all(
            Stock.objects.filter(sucursal=tienda, producto_id=producto_id, cantidad__gt=0).exists()
            for producto_id in productos_ids
        )
        if tiene_todos_productos:
            tiendas_validas.append(tienda)

    # Formatear total_carrito_clp y total_carrito según la divisa seleccionada
    if currency == 'CLP':
        total_carrito_formatted = f"${intcomma(int(total_carrito_clp))} CLP"
    else:
        total_carrito_formatted = f"${floatformat(total_carrito, 2)} USD"

    context = {
        "carrito_dict": carrito_dict,
        "total_carrito": total_carrito,
        "total_carrito_formatted": total_carrito_formatted,
        "neto": intcomma(int(neto)),
        "iva": intcomma(int(iva)),
        "form": form,
        "envio_datos": request.session.get('envio_datos', {}),
        "tiendas_validas": tiendas_validas,
        "currency": currency,
    }

    return render(request, 'app/envio.html', context)
@login_required
def revisar_pedidos(request):
    pedidos = Pedido.objects.filter(email=request.user.email)
    
    currency = request.session.get('currency', 'CLP')
    mindicador = Mindicador('dolar')
    dollar_value = mindicador.get_dollar_value_today()

    pedidos_detalles = []

    for pedido in pedidos:
        total_pedido = pedido.detallepedido_set.aggregate(total=Sum('precio_total'))['total']
        pedido.total_pedido = total_pedido if total_pedido else 0

        detalles = []
        for detalle in pedido.detallepedido_set.all():
            if currency == 'USD' and dollar_value:
                detalle_precio_unitario = detalle.precio_unitario / dollar_value
                detalle_precio_total = detalle.precio_total / dollar_value
                detalle_precio_unitario_formatted = f"${detalle_precio_unitario:,.2f} USD"
                detalle_precio_total_formatted = f"${detalle_precio_total:,.2f} USD"
            else:
                detalle_precio_unitario_formatted = f"${detalle.precio_unitario:,} CLP"
                detalle_precio_total_formatted = f"${detalle.precio_total:,} CLP"
            
            detalles.append({
                'producto_nombre': detalle.producto_nombre,
                'cantidad': detalle.cantidad,
                'precio_unitario_formatted': detalle_precio_unitario_formatted,
                'precio_total_formatted': detalle_precio_total_formatted,
                'imagen_url': detalle.imagen_url
            })
        
        if currency == 'USD' and dollar_value:
            pedido_total_pedido_formatted = f"${pedido.total_pedido / dollar_value:,.2f} USD"
        else:
            pedido_total_pedido_formatted = f"${pedido.total_pedido:,} CLP"

        pedidos_detalles.append({
            'numero_pedido': pedido.numero_pedido,
            'fecha': pedido.fecha,
            'total_pedido_formatted': pedido_total_pedido_formatted,
            'detalles': detalles,
            'nombre': pedido.nombre,
            'direccion': pedido.direccion,
            'ciudad': pedido.ciudad,
            'region': pedido.region,
            'codigo_postal': pedido.codigo_postal,
            'pais': pedido.pais,
            'telefono': pedido.telefono,
            'metodo_envio': pedido.metodo_envio
        })

    context = {
        'pedidos_detalles': pedidos_detalles,
        'currency': currency,
        'dollar_value': dollar_value,
    }
    return render(request, 'app/revisar_pedidos.html', context)

def set_currency(request, currency):
    request.session['currency'] = currency
    return redirect(request.META.get('HTTP_REFERER', 'index'))
