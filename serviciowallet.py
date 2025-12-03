# Archivo para manejar la creación, carga y uso de una wallet
# De sumna importancia para poder hacer un tipo puente entre la interfaz 
# Y el archivo de almallave 

from almacen_claves import (
    crear_archivo_keystore,
    cargar_archivo_keystore,
    firmar_datos_con_clave_privada
)


class ServicioWallet:

    def __init__(self):
        self.wallet_cargada = None  # Guardará la clave privada y pública

    #  Aquí creamos una nueva wallet

    def crear_nueva_wallet(self, ruta_archivo, contrasena):

        crear_archivo_keystore(ruta_archivo, contrasena)
        print(f"[OK] Wallet creada y guardada en: {ruta_archivo}")

    # 2) Creamos una wallet existente

    def cargar_wallet_existente(self, ruta_archivo, contrasena):

        claves = cargar_archivo_keystore(ruta_archivo, contrasena)
        self.wallet_cargada = claves
        print(f"[OK] Wallet cargada desde: {ruta_archivo}")


    # 3) Obtenemos una dirección publica

    def obtener_direccion_publica(self):

        if not self.wallet_cargada:
            raise Exception("No hay wallet cargada.")
        return self.wallet_cargada["clave_publica"]


    # 4) Firmar un mensaje

    def firmar_mensaje(self, mensaje):

        if not self.wallet_cargada:
            raise Exception("No hay wallet cargada.")

        firma = firmar_datos_con_clave_privada(
            self.wallet_cargada["clave_privada"],
            mensaje
        )
        return firma
