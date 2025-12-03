# Este archivo define la parte de la estructura interna de la wallet.
# Aquí representamos una wallet como un objeto con sus datos y funciones principales.


class Wallet:

    def __init__(self, clave_publica, clave_privada=None, direccion=None, descripcion=""):


        self.clave_publica = clave_publica
        self.clave_privada = clave_privada
        self.direccion = direccion
        self.descripcion = descripcion

        # Aquí se podría almacenar también el balance si el sistema lo requiere.
        # Por ahora, lo dejamos como None.
        self.balance = None


    # Aquí van las funciones principales de la wallet


    def obtener_direccion(self):

        return self.direccion

    #esta funcion de actualizar descripción permite que se pueda actualizar la parte de la descripcion de una wallet
    
    def actualizar_descripcion(self, nuevo_texto):

        self.descripcion = nuevo_texto

    def tiene_clave_privada(self):

        return self.clave_privada is not None

    def como_diccionario(self):

        return {
            "clave_publica": self.clave_publica,
            "direccion": self.direccion,
            "descripcion": self.descripcion,
            "balance": self.balance
        }

    # Funciones opcional que es lo de la firma de datos 


    def firmar(self, datos, funcion_firmado):

        if not self.tiene_clave_privada():
            raise Exception("La wallet no tiene clave privada cargada. No puede firmar datos.")

        return funcion_firmado(self.clave_privada, datos)
