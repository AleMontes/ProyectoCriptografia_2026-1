import os
from typing import Optional

# En esta parte importamos los módulos del proyecto

from almacen_llaves import create_keystore_file, load_keystore_file
from servicio_wallet import ServicioWallet
from modelo_wallet import Wallet


class GestorWallet:

    def __init__(self):

        self.servicio_wallet = ServicioWallet()


    # Creo una función para crear una wallet nueva

    def crear_wallet_nueva(self, ruta_keystore: str, passphrase: str,
                           descripcion: str = "Wallet generada por el sistema") -> Wallet:


        # Creamos el archivo keystore (usa Argon2id + AES-GCM)
        datos_keystore = create_keystore_file(ruta_keystore, passphrase)

        # Extraemos la llave pública del archivo generado
        pub_bytes = datos_keystore["pubkey_b64"]

        # Pedimos al servicio que derive la dirección
        direccion = self.servicio_wallet.generar_direccion_desde_pubkey(pub_bytes)

        # Creamos el modelo Wallet, que es lo que el usuario manipula
        wallet = Wallet(
            direccion=direccion,
            ruta_keystore=ruta_keystore,
            descripcion=descripcion,
            pubkey_b64=pub_bytes
        )

        return wallet


    # CReo una función para poder cargar una wallet existente

    def cargar_wallet(self, ruta_keystore: str, passphrase: str) -> Wallet:

        if not os.path.exists(ruta_keystore):
            raise FileNotFoundError(f"No existe el archivo keystore en: {ruta_keystore}")

        llave_privada, pub_bytes, metadata = load_keystore_file(ruta_keystore, passphrase)

        # Generar dirección
        direccion = self.servicio_wallet.generar_direccion_desde_pubkey(pub_bytes)

        # Crear objeto Wallet en memoria
        wallet = Wallet(
            direccion=direccion,
            ruta_keystore=ruta_keystore,
            descripcion=metadata.get("descripcion", "Wallet importada"),
            pubkey_b64=metadata["pubkey_b64"],
            llave_privada_obj=llave_privada  # opcional, se puede guardar para firmar
        )

        return wallet

    # Otra función pero esta es para poder Firmar todos los datos

    def firmar_mensaje(self, wallet: Wallet, mensaje: bytes, passphrase: Optional[str] = None) -> bytes:

        if wallet.llave_privada_obj is None:
            if passphrase is None:
                raise ValueError("Se requiere la passphrase para cargar la llave privada.")
            self._cargar_llave_privada_en_wallet(wallet, passphrase)

        firma = self.servicio_wallet.firmar(wallet.llave_privada_obj, mensaje)
        return firma


    # Función para poder verificar una firma

    def verificar_firma(self, wallet: Wallet, mensaje: bytes, firma: bytes) -> bool:


        return self.servicio_wallet.verificar(wallet.pubkey_bytes(), mensaje, firma)

    # Esta es una función interna para poder cargar llave privada en la wallet

    def _cargar_llave_privada_en_wallet(self, wallet: Wallet, passphrase: str):

        llave_privada, pub_bytes, metadata = load_keystore_file(wallet.ruta_keystore, passphrase)
        wallet.llave_privada_obj = llave_privada  # Guardamos temporalmente
