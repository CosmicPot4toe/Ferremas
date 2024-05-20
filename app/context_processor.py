def carro_home(request):
    total = 0
    if "carrito" in request.session.keys():
            for key, value in request.session["carrito"].items():
                total += 1
    return {"carro_home": total}

def total_carrito(request):
    total = 0
    if "carrito" in request.session.keys():
        for item in request.session["carrito"].values():
            total += item["precio_total"]
    return {"total_carrito": total}
