class Precios:
    @staticmethod #decorador: definir un metodo estatico (no dende de una instancia particular de la clase (no accede a self))
    def calcular_precio_final(precio_base, impuesto, descuento):
        return precio_base+impuesto-descuento