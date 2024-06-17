from datetime import datetime, timezone
from datetime import datetime
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages as msgs
from django.urls import reverse
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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def buscar(request):
    query = request.GET.get('q')
    filtro_precio = request.GET.get('precio')
    filtro_marca = request.GET.get('marca')
    filtro_categoria = request.GET.get('categoria')

    resultados = Producto.objects.all()

    if query:
        resultados = resultados.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(marca__icontains=query) |
            Q(categoria__nombre_categoria__icontains=query) |
            Q(categoria__subcategoria__icontains=query) |
            Q(categoria__sub_tipo_producto__icontains=query)
        ).distinct()

    if filtro_precio:
        precios = filtro_precio.split('-')
        if len(precios) == 2:
            resultados = resultados.filter(precio__gte=precios[0], precio__lte=precios[1])
        elif len(precios) == 1:
            resultados = resultados.filter(precio__gte=precios[0])

    if filtro_marca:
        resultados = resultados.filter(marca=filtro_marca)

    if filtro_categoria:
        resultados = resultados.filter(categoria__nombre_categoria=filtro_categoria)

    mindicador = Mindicador('dolar')
    dollar_value = mindicador.get_dollar_value_today()
    currency = request.session.get('currency', 'CLP')

    for producto in resultados:
        if currency == 'USD' and dollar_value:
            producto.precio = producto.precio / dollar_value

    marcas = Producto.objects.values_list('marca', flat=True).distinct()
    categorias = Producto.objects.values_list('categoria__nombre_categoria', flat=True).distinct()

    return render(request, 'app/buscar.html', {
        'resultados': resultados,
        'query': query,
        'currency': currency,
        'marcas': marcas,
        'categorias': categorias,
    })


def index(request):
    # Obtener los últimos 5 productos añadidos, ordenados por id_producto descendente
    #productos = Producto.objects.all().order_by('-id_producto')[:5]
    productos = PhpApi('Producto').getAll()[-5:]
    mindicador = Mindicador('dolar')
    dollar_value = mindicador.get_dollar_value_today()
    currency = request.session.get('currency', 'CLP')
    for producto in productos:
        if currency == 'USD' and dollar_value:
            producto['precio']= producto['precio'] / dollar_value

    data ={
        'productos': productos,
        'currency': currency,
        'dollar_value':dollar_value
    }
    return render(request, 'app/index.html', data)

def detalle_producto(request, id):
    producto = get_object_or_404(Producto, id_producto=id)
    mindicador = Mindicador('dolar')
    dollar_value = mindicador.get_dollar_value_today()
    currency = request.session.get('currency', 'CLP')

    if currency == 'USD' and dollar_value:
        producto.precio = producto.precio / dollar_value

    categoria_producto = producto.categoria
    categoria = categoria_producto.categoria
    stocks = Stock.objects.filter(producto=producto)
    stocks_por_tienda = {}

    for stock in stocks:
        tienda = stock.sucursal.nombre
        cantidad = stock.cantidad
        if tienda in stocks_por_tienda:
            stocks_por_tienda[tienda] += cantidad
        else:
            stocks_por_tienda[tienda] = cantidad

    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        carrito = Carrito(request)
        action = request.POST.get('action')

        if action == 'add_to_cart':
            carrito.agregar(producto, cantidad=cantidad)
            return redirect('carrito')
        elif action == 'buy_now':
            carrito.vaciar()
            carrito.agregar(producto, cantidad=cantidad)
            return redirect('envio')

    data = {
        'producto': producto,
        'id_categoria': categoria.id_categoria,
        'nombre_categoria': categoria.nombre,
        'stocks_por_tienda': stocks_por_tienda,
        'currency': currency,
    }
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
    return redirect("carrito")

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

    mindicador = Mindicador('dolar')
    dollar_value = mindicador.get_dollar_value_today()
    currency = request.session.get('currency', 'CLP')

    for key, value in carrito_dict.items():
        producto = Producto.objects.get(id_producto=int(key))
        value["marca"] = producto.marca

        if currency == 'USD' and dollar_value:
            value["precio_unitario"] = value["precio_unitario"] / dollar_value
            value["precio_total"] = value["precio_total"] / dollar_value

        value["precio_unitario_formatted"] = floatformat(value["precio_unitario"], 2) if currency == 'USD' else intcomma(value["precio_unitario"])
        value["precio_total_formatted"] = floatformat(value["precio_total"], 2) if currency == 'USD' else intcomma(value["precio_total"])

        total_carrito += value["precio_total"]

    total_carrito_clp = total_carrito if currency == 'CLP' else total_carrito * dollar_value
    iva = total_carrito_clp * 0.19
    neto = total_carrito_clp * 0.81

    if request.method == 'POST':
        form = DetalleEnvioForm(request.POST)
        if form.is_valid():
            envio_datos = form.cleaned_data
            request.session['envio_datos'] = envio_datos

            metodo_envio = 'envio-internacional' if envio_datos['pais'] != 'cl' else request.POST.get('metodo_envio', '')
            tienda_seleccionada_id = request.POST.get('tienda_select', '')

            if metodo_envio == 'retiro-tienda' and tienda_seleccionada_id:
                tienda_seleccionada = Tienda.objects.get(id_tienda=tienda_seleccionada_id).nombre
                estado_envio = 'Por Confirmar'
            else:
                tienda_seleccionada = ''
                estado_envio = 'Por Confirmar'

            buy_order = str(random.randrange(1000000, 99999999))
            session_id = str(random.randrange(1000000, 99999999))
            return_url = request.build_absolute_uri(reverse('commit'))

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
                producto = Producto.objects.get(id_producto=int(key))
                detalle_pedido = DetallePedido(
                    pedido=pedido,
                    producto_nombre=value["nombre"],
                    cantidad=value["cantidad"],
                    precio_unitario=producto.precio,
                    precio_total=producto.precio * value["cantidad"],
                    imagen_url=value["imagen_url"],
                    estado_envio=estado_envio
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
                'imagen_url': detalle.imagen_url,
                'estado_envio': detalle.estado_envio
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

    # Obtener productos recomendados
    productos_recomendados = list(Producto.objects.all())
    random.shuffle(productos_recomendados)
    productos_recomendados = productos_recomendados[:3]  # Mostrar 4 productos recomendados  # Ejemplo: seleccionar los primeros 3 productos

    productos_recomendados_data = []
    for producto in productos_recomendados:
        if currency == 'USD' and dollar_value:
            producto_precio_formatted = f"${producto.precio / dollar_value:,.2f} USD"
        else:
            producto_precio_formatted = f"${producto.precio:,} CLP"

        productos_recomendados_data.append({
            'id': producto.id_producto,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'imagen_url': producto.imagen_url,
            'precio_formatted': producto_precio_formatted,
        })

    context = {
        'pedidos_detalles': pedidos_detalles,
        'currency': currency,
        'dollar_value': dollar_value,
        'productos_recomendados': productos_recomendados_data,
    }
    return render(request, 'app/revisar_pedidos.html', context)

def set_currency(request, currency):
    request.session['currency'] = currency
    return redirect(request.META.get('HTTP_REFERER', 'index'))

def contacto (request):
    data = {
        'form': ContactosFrom()
    }

    if request.method == 'POST':
        formulario = ContactosFrom (data=request.POST)
        if formulario.is_valid():
            formulario.save()
            msgs.success(request,"¡Enviado correctamente! Recibira su respuesta a su correo electronico en breve!")
            return redirect(to="index")
        else:
            data["form"] = formulario

    return render(request, 'app/contacto.html',data )


def nosotros (request):
    return render(request, 'app/nosotros.html')

def add_and_checkout(request, Producto_id_producto):
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))  # Obtener la cantidad del formulario POST
        carrito = Carrito(request)
        producto = Producto.objects.get(id_producto=Producto_id_producto)
        carrito.agregar(producto, cantidad=cantidad)  # Pasar la cantidad al método agregar
        return redirect('envio')  # Redirigir a la página de método de envío
    else:
        # Manejar el caso en que no se reciba una solicitud POST
        # Por ejemplo, redirigir o mostrar un mensaje de error
        return HttpResponse("Método no permitido")
    
#cuenta de bodeguero bodeguero@ferremas.cl y contra Cavernicola1618

@login_required
def pedidos_pendientes(request):
    if request.user.type != 'Bod':
        return redirect('login')
    
    pedidos = DetallePedido.objects.filter(estado_envio__in=['Por Enviar', 'Por Retirar'])
    
    page = request.GET.get('page', 1)
    paginator = Paginator(pedidos, 5)
    
    try:
        pedidos = paginator.page(page)
    except PageNotAnInteger:
        pedidos = paginator.page(1)
    except EmptyPage:
        pedidos = paginator.page(paginator.num_pages)
    
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        pedido = get_object_or_404(DetallePedido, id=pedido_id)
        form = ActualizarEstadoEnvioForm(request.POST, instance=pedido)
        
        if form.is_valid():
            form.save()
            return redirect('pedidos_pendientes')
    else:
        form = ActualizarEstadoEnvioForm()
    
    context = {
        'pedidos': pedidos,
        'paginator': paginator,
        'form': form,
    }
    
    return render(request, 'bodeguero/pedidos_pendientes.html', context)

def actualizar_estado_envio(request, detalle_pedido_id):
    detalle_pedido = get_object_or_404(DetallePedido, id=detalle_pedido_id)

    if request.method == 'POST':
        form = ActualizarEstadoEnvioForm(request.POST, instance=detalle_pedido)
        if form.is_valid():
            form.save()
            return redirect('pedidos_pendientes')
    else:
        form = ActualizarEstadoEnvioForm(instance=detalle_pedido)

    context = {
        'form': form,
        'detalle_pedido': detalle_pedido,
    }
    return render(request, 'bodeguero/actualizar_estado_envio.html', context)



@login_required
def admin_dashboard(request):
    if request.user.type != 'Adm':
        return redirect('login')
    
    query = request.GET.get('q')
    if query:
        productos = Producto.objects.filter(
            Q(marca__icontains=query) | 
            Q(nombre__icontains=query) | 
            Q(categoria__nombre_categoria__icontains=query)
        )
    else:
        productos = Producto.objects.all()

    paginator = Paginator(productos, 5)  # Muestra 10 productos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    users = User.objects.all()
    tiendas = Tienda.objects.all()
    categorias = Categoria.objects.all()
    stock = Stock.objects.all()
    categoria_producto= CategoriaProducto.objects.all()

    user_form = UserForm()
    producto_form = ProductoForm()
    tienda_form = TiendaForm()
    categoria_form = CategoriaForm()
    stock_form = StockForm()

    context = {
        'productos': productos,
        'users': users,
        'page_obj': page_obj,
        'tiendas': tiendas,
        'categorias': categorias,
        'categoria_producto': categoria_producto,
        'stocks': stock,
        'user_form': user_form,
        'producto_form': producto_form,
        'tienda_form': tienda_form,
        'categoria_form': categoria_form,
        'stock_form': stock_form,
        'query': query
    }
    return render(request, 'admin/admin_dashboard.html', context)

def create_user(request):
    if request.method == 'POST':
        form = RegUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.type = 'Cli'  # Asignar el valor predeterminado para type
            user.save()
            username = form.cleaned_data.get('username')
            msgs.success(request, f'Cuenta creada exitosamente para {username}. ¡Ahora puedes iniciar sesión!')
            return redirect('admin_dashboard')

        else:
            form = RegUserForm()
    return JsonResponse({'success': False})

def update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            username = user.username
            msgs.info(request, f'¡La cuenta de {username} ha sido modificada correctamente!')
            return redirect('admin_dashboard')
    else:
        data = {
            'success': True,
            'username': user.username,
            'email': user.email,
            'type': user.type
        }
        return JsonResponse(data)
    return redirect('admin_dashboard')


def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    username=user.username
    user.delete()
    msgs.warning(request, f'La cuenta {username} fue eliminada.')
    return redirect('admin_dashboard')

def create_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            msgs.success(request, f'Producto creado exitosamente!')
        return redirect('admin_dashboard')
    return JsonResponse({'success': False})

def update_producto(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            msgs.info(request, f'¡Producto modiciado correctamente!')
            return redirect('admin_dashboard')
    else:
        form = ProductoForm(instance=producto)
    return JsonResponse({'success': False, 'form': form.as_p()})

def get_producto(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    data = {
        'success': True,
        'marca': producto.marca,
        'nombre': producto.nombre,
        'codigo_producto': producto.codigo_producto,
        'descripcion': producto.descripcion,
        'precio': producto.precio,
        'categoria': producto.categoria.id if producto.categoria else None,
        'imagen_url': producto.imagen_url,
    }
    return JsonResponse(data)

def delete_producto(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    product_name=producto.nombre
    producto.delete()
    msgs.warning(request, f'El producto {product_name} fue eliminado')
    return redirect('admin_dashboard')

def create_tienda(request):
    if request.method == 'POST':
        form = TiendaForm(request.POST)
        if form.is_valid():
            form.save()
            nombre_tienda = form.cleaned_data.get('nombre')
            msgs.success(request, f'La tienda {nombre_tienda} fue creada correctamente. ')
        return redirect('admin_dashboard')
    return JsonResponse({'success': False})


def get_tienda(request, tienda_id):
    tienda = get_object_or_404(Tienda, id_tienda=tienda_id)
    data = {
        'success': True,
        'nombre': tienda.nombre,
        'direccion': tienda.direccion,
        'comuna': tienda.comuna,
        'region': tienda.region,
        'telefono': tienda.telefono,
        'email': tienda.email,
    }
    return JsonResponse(data)

def update_tienda(request, tienda_id):
    tienda = get_object_or_404(Tienda, id_tienda=tienda_id)
    if request.method == 'POST':
        form = TiendaForm(request.POST, instance=tienda)
        if form.is_valid():
            form.save()
            nombre_tienda = form.cleaned_data.get('nombre')
            msgs.info(request, f'La tienda {nombre_tienda} fue actualizada conrrectamente.')
        return redirect('admin_dashboard')
    else:
        form = TiendaForm(instance=tienda)
    return JsonResponse({'success': False, 'form': form.as_p()})

def delete_tienda(request, tienda_id):
    tienda = get_object_or_404(Tienda, id_tienda=tienda_id)
    nombre_tienda = tienda.nombre
    tienda.delete()
    msgs.warning(request, f'La tienda {nombre_tienda} fue eliminada correctamente. ')
    return redirect('admin_dashboard')

def create_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            nombre_categoria = form.cleaned_data.get('nombre')
            msgs.success(request, f'La tienda {nombre_categoria} fue creada correctamente. ')
        return redirect('admin_dashboard')
    else:
        msgs.error(request, f'La operación no se pudo realizar.')
        return redirect('admin_dashboard')
        

def update_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id_categoria=categoria_id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            nombre_categoria = form.cleaned_data.get('nombre')
            msgs.info(request, f'La categoria {nombre_categoria} fue actualizada.')
        return redirect('admin_dashboard')
    else:
        form = CategoriaForm(instance=categoria)
    return JsonResponse({'success': False, 'form': form.as_p()})

def get_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id_categoria=categoria_id)
    data = {
        'success': True,
        'nombre': categoria.nombre
    }
    return JsonResponse(data)

def delete_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id_categoria=categoria_id)
    categoria.delete()
    msgs.warning(request, f'La categoria {categoria.nombre} fue eliminada. ')
    return redirect('admin_dashboard')

def create_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            nombre_producto = form.cleaned_data.get('producto')
            cantidad = form.cleaned_data.get('cantidad')
            sucursal = form.cleaned_data.get('sucursal')
            msgs.success(request, f'Stock de {cantidad} de producto {nombre_producto} en sucursal {sucursal} añadido. ')
        return redirect('admin_dashboard')
    return JsonResponse({'success': False})

def get_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    data = {
        'success': True,
        'sucursal': stock.sucursal.id_tienda,
        'producto_id': stock.producto.id_producto,  # Asegúrate de devolver el ID del producto
        'cantidad': stock.cantidad,
    }
    return JsonResponse(data)


def update_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            msgs.info(request, 'El stock fue actualizado correctamente.')
        return redirect('admin_dashboard')
    else:
        form = StockForm(instance=stock)
    return JsonResponse({'success': False, 'form': form.as_p()})

def delete_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    stock.delete()
    return redirect('admin_dashboard')