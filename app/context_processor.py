def carro_home(request):
    total = 0
    if "carrito" in request.session.keys():
            for key, value in request.session["carrito"].items():
                total += 1
    return {"carro_home": total}

def total_carrito(request):
    total = 0
    if "carrito" in request.session.keys():
        for key, value in request.session["carrito"].items():
            # Calcula el precio individual multiplicando el precio base del producto por la cantidad
            value["precio_individual"] = value["precio"] * value["cantidad"]
            total += value["precio_individual"]  # Ahora sumamos los precios individuales
    return {"total_carrito": total}

