#Este archivo define la clase Wallet, que funciona como un "modelo" por así decirlo o
#estructura de datos que representa una billetera dentro de nuestro sistema.
#este archivo es la actualizacion del primer modelowallet que subi
#resuelve el issue

class Wallet:


    def __init__(self, direccion: str, llave_publica: bytes, llave_privada=None, ruta_archivo=None):

        self.direccion = direccion
        self.llave_publica = llave_publica
        self.llave_privada = llave_privada
        self.ruta_archivo = ruta_archivo

    # Métodos auxiliares básicos

    def tiene_llave_privada(self) -> bool:

        return self.llave_privada is not None

    def borrar_llave_privada(self):

        try:
            if isinstance(self.llave_privada, bytearray):
                # Método más seguro para borrar
                for i in range(len(self.llave_privada)):
                    self.llave_privada[i] = 0
            self.llave_privada = None
        except Exception:
            # En caso de algún error, igual quitamos la referencia
            self.llave_privada = None

    # Representación de la wallet


    def __repr__(self):

        return (
            f"Wallet(direccion='{self.direccion}', "
            f"llave_publica={self.llave_publica.hex()}, "
            f"ruta_archivo='{self.ruta_archivo}', "
            f"tiene_llave_privada={self.tiene_llave_privada()})"
        )
