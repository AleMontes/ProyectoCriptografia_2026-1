import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from app.canonicalizer import canonicalize

class Signer:
    def __init__(self, private_key: Ed25519PrivateKey):
        """
        El Signer recibe una llave privada cargada
        (no el archivo, sino el objeto llave)
        """
        self.private_key = private_key

    def sign_transaction(self, transaction):
        """
        Toma una instancia de Transaction, la canonicaliza y la firma
        Retorna el diccionario listo para guardarse en el JSON
        """
        # Convertir Transacción a Diccionario y luego a Bytes Canonicos
        tx_dict = transaction.to_dict()
        tx_bytes = canonicalize(tx_dict)

        # Firmar (Ed25519)
        signature = self.private_key.sign(tx_bytes)

        # Obtener la llave pública para adjuntarla 
        public_key = self.private_key.public_key()
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

        return {
            "tx": tx_dict,
            "sig_scheme": "Ed25519",
            "signature_b64": base64.b64encode(signature).decode('utf-8'),
            "pubkey_b64": base64.b64encode(public_bytes).decode('utf-8')
        }