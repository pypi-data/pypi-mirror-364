class Cliente:
    clientes_creados = 0  # Atributo de clase

    def __init__(self, nombre, email, direccion, telefono):
        self.nombre = nombre
        self.email = email
        self.direccion = direccion
        self.telefono = telefono
        Cliente.clientes_creados += 1

    def __str__(self):
        return f"Cliente: {self.nombre} - Email: {self.email}"

    def actualizar_direccion(self, nueva_direccion):
        self.direccion = nueva_direccion

    def mostrar_info(self):
        return (f"Nombre: {self.nombre}\n"
                f"Email: {self.email}\n"
                f"Dirección: {self.direccion}\n"
                f"Teléfono: {self.telefono}")
