class Carrito:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        carrito = self.session.get("carrito")
        if not carrito:
            self.session["carrito"] = {}
            self.carrito = self.session["carrito"]
        else:
            self.carrito = carrito

    def obtener_cantidad_productos(self):
        cantidad_total = sum(item["cantidad"] for item in self.carrito.values())
        return cantidad_total

    def agregar(self, producto, cantidad=1):
        id_producto = str(producto.id_producto)
        if id_producto not in self.carrito.keys():
            self.carrito[id_producto] = {
                "id": producto.id_producto,
                "nombre": producto.nombre,
                "precio_unitario": producto.precio,
                "cantidad": cantidad,
                "precio_total": producto.precio * cantidad,
                "imagen_url": producto.imagen_url  # Asegúrate de tener esta línea si necesitas la imagen
            }
        else:
            self.carrito[id_producto]["cantidad"] += cantidad
            self.carrito[id_producto]["precio_total"] = self.carrito[id_producto]["precio_unitario"] * self.carrito[id_producto]["cantidad"]
        self.guardar_carrito()

    def guardar_carrito(self):
        self.session["carrito"] = self.carrito
        self.session.modified = True

    def eliminar(self, Producto):
        id_producto = str(Producto.id_producto)
        if id_producto in self.carrito:
            del self.carrito[id_producto]
            self.guardar_carrito()

    def restar(self, Producto):
        id_producto = str(Producto.id_producto)
        if id_producto in self.carrito.keys():
            self.carrito[id_producto]["cantidad"] -= 1
            self.carrito[id_producto]["precio_total"] = self.carrito[id_producto]["precio_unitario"] * self.carrito[id_producto]["cantidad"]
            if self.carrito[id_producto]["cantidad"] <= 0:
                self.eliminar(Producto)
            self.guardar_carrito()

    def limpiar(self):
        self.session["carrito"] = {}
        self.session.modified = True
        
    def vaciar(self):
        self.carrito = {}
        self.guardar_carrito()
