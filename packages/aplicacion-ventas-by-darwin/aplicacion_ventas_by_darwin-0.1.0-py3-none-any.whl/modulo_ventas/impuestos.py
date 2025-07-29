from .exceptions import ImpuestoInvalidoError

class Impuestos:
    def __init__ (self, porcentaje): #costructor
        if not (0<=porcentaje<=1): #validacion
            raise ImpuestoInvalidoError ("La tasa de impuestos debe estar entre 0 y 1.")
        self.porcentaje=porcentaje
    
    def aplicar_impuesto(self, precio):
        return precio * self.porcentaje