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


    def agregar(self, producto, cantidad=1):  # Modificar para aceptar cantidad como parámetro
        id_producto = str(producto.id_producto)
        if id_producto not in self.carrito.keys():
            self.carrito[id_producto] = {
                "id": producto.id_producto,
                "nombre": producto.nombre,
                "precio": producto.precio,
                "cantidad": cantidad,  # Utilizar la cantidad proporcionada
            }
        else:
            self.carrito[id_producto]["cantidad"] += cantidad  # Sumar la cantidad proporcionada
            self.carrito[id_producto]["precio"] += producto.precio * cantidad  # Actualizar el precio total
        self.guardar_carrito()

    def guardar_carrito(self):
        self.session["carrito"] = self.carrito
        self.session.modified = True

    def eliminar(self, Producto):
        id_producto = str(Producto.id_producto)
        if id_producto in self.carrito:
            del self.carrito[id_producto]
            self.guardar_carrito()

    def restar(self,Producto):
        id_producto = str(Producto.id_producto)
        if id_producto in self.carrito.keys():
            self.carrito[id_producto]["cantidad"] -= 1
            self.carrito[id_producto]["precio"] -= Producto.precio
            if self.carrito[id_producto]["cantidad"] <= 0:
                self.eliminar(Producto)
            self.guardar_carrito()

    def limpiar(self):
        self.session["carrito"] = {}
        self.session.modified = True