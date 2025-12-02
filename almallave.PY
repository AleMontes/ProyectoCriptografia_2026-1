# Librerías esenciales para implementar la funcionalidad del
# keystore (almacenamiento seguro de llaves privadas).

import os
import json
import base64
import datetime
import hashlib
import stat
import gc

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from argon2.low_level import hash_secret_raw, Type as ArgonType
import sha3   # de la librería pysha3 (para keccak256)


# Aqui empiezan ls utildades generales (base64, fechas, permisos)


def a_base64(b: bytes) -> str:
    """Convierte bytes a texto Base64."""
    return base64.b64encode(b).decode('ascii')

def de_base64(s: str) -> bytes:
    """Convierte un string Base64 a bytes."""
    return base64.b64decode(s.encode('ascii'))

def now_iso_z():

    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def establecer_permiso_solo_usuario(path: str):

    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


# Generación de las llaves Ed25519
 #   Genera un par de llaves Ed25519 (pública y privada) y las devuelve en bytes. 

def generar_par_ed25519():
   
    priv = ed25519.Ed25519PrivateKey.generate()
    pub = priv.public_key()

    # Serialización "raw" de Ed25519
    priv_bytes = priv.private_bytes(
        encoding=None,
        format=None,
        encryption_algorithm=None
    )

    # Repetimos serialización con valores explícitos
    priv_bytes = priv.private_bytes(
        encoding=1,
        format=1,
        encryption_algorithm=0
    )

    pub_bytes = pub.public_bytes(
        encoding=1,
        format=3
    )
    return priv_bytes, pub_bytes

from cryptography.hazmat.primitives import serialization

def generar_par_ed25519_raw():

    priv = ed25519.Ed25519PrivateKey.generate()
    priv_bytes = priv.private_bytes(
        encoding = serialization.Encoding.Raw,
        format = serialization.PrivateFormat.Raw,
        encryption_algorithm = serialization.NoEncryption()
    )
    pub = priv.public_key()
    pub_bytes = pub.public_bytes(
        encoding = serialization.Encoding.Raw,
        format = serialization.PublicFormat.Raw
    )
    return priv, priv_bytes, pub_bytes

# Derivación de claves (KDF) con Argon2id


def derivar_clave_argon2(passphrase: str, salt: bytes,
                         time_cost: int = 2, memory_cost_kib: int = 131072,
                         parallelism: int = 1, longitud: int = 32) -> bytes:

    if isinstance(passphrase, str):
        pass_bytes = passphrase.encode('utf-8')
    else:
        pass_bytes = passphrase

    clave = hash_secret_raw(
        secret = pass_bytes,
        salt = salt,
        time_cost = time_cost,
        memory_cost = memory_cost_kib,
        parallelism = parallelism,
        hash_len = longitud,
        type = ArgonType.ID
    )
    return clave

# -------------------------------------------------------------
# Alternativa PBKDF2 en caso de no tener Argon2 es más antiguo pero por si las moscas
# -------------------------------------------------------------

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

def derivar_clave_pbkdf2(passphrase: str, salt: bytes,
                         iteraciones: int = 200000, longitud: int = 32) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm = hashes.SHA256(),
        length    = longitud,
        salt      = salt,
        iterations= iteraciones,
        backend   = default_backend()
    )
    return kdf.derive(passphrase.encode('utf-8'))


# Cifrado AES-GCM (AES-256-GCM)
#   Cifra la llave privada usando AES-256-GCM, el modo GCM provee la parte de la autenticación e integridad.

def cifrar_llave_privada(priv_bytes: bytes, clave: bytes, nonce: bytes):
  
    aes = AESGCM(clave)
    ct = aes.encrypt(nonce, priv_bytes, None)

    tag = ct[-16:]
    ciphertext = ct[:-16]
    return ciphertext, tag

def descifrar_llave_privada(ciphertext: bytes, tag: bytes,
                            clave: bytes, nonce: bytes):
    aes = AESGCM(clave)
    return aes.decrypt(nonce, ciphertext + tag, None)


# Derivación de dirección estilo Ethereum (keccak256)
# Crea una dirección tipo Ethereum tomando los últimos 20 bytes del hash keccak256 de la llave pública.


def derivar_direccion_keccak(pubkey_bytes: bytes) -> str:
    
    k = sha3.keccak_256()
    k.update(pubkey_bytes)
    h = k.digest()
    direccion = h[12:]
    return "0x" + direccion.hex()


# Checksum del archivo JSON (sin incluir el campo checksum)


def generar_checksum(obj: dict, excluir: str = "checksum_hex") -> str:
    """
    Genera un SHA-256 del JSON ordenado alfabéticamente.
    Sirve para detectar modificaciones al archivo.
    """
    copia = {k: v for k, v in obj.items() if k != excluir}
    canonico = json.dumps(
        copia, sort_keys=True, separators=(',', ':'), ensure_ascii=False
    ).encode('utf-8')

    return hashlib.sha256(canonico).hexdigest()


# Crear y cargar keystore
# Crea un archivo keystore seguro que contiene la llave privada cifrada.
# Este parte es de siuma imoptancia ya que es lo que después se guarda como wallet.

def crear_keystore(path: str, passphrase: str,
                   esquema: str = "Ed25519",
                   kdf_params=None,
                   cifrado="AES-256-GCM"):
   

    # 1) Generar par de llaves
    priv_obj, priv_bytes, pub_bytes = generar_par_ed25519_raw()

    # 2) Generar un salt aleatorio
    salt = os.urandom(16)

    # 3) Derivar la clave con Argon2id
    if kdf_params is None:
        kdf_params = {
            "time_cost": 2,
            "memory_cost_kib": 131072,
            "parallelism": 1
        }

    clave_derivada = derivar_clave_argon2(
        passphrase,
        salt,
        time_cost=kdf_params["time_cost"],
        memory_cost_kib=kdf_params["memory_cost_kib"],
        parallelism=kdf_params["parallelism"],
        longitud=32
    )

    # 4) Generar un nonce para AES-GCM
    nonce = os.urandom(12)

    # 5) Cifrar la llave privada
    ciphertext, tag = cifrar_llave_privada(priv_bytes, clave_derivada, nonce)

    # 6) Construir el objeto JSON
    obj = {
        "kdf": "Argon2id",
        "kdf_params": {
            "salt_b64": a_base64(salt),
            "time_cost": kdf_params["time_cost"],
            "memory_cost_kib": kdf_params["memory_cost_kib"],
            "parallelism": kdf_params["parallelism"]
        },
        "cipher": cifrado,
        "cipher_params": { "nonce_b64": a_base64(nonce) },
        "ciphertext_b64": a_base64(ciphertext),
        "tag_b64": a_base64(tag),
        "pubkey_b64": a_base64(pub_bytes),
        "created": now_iso_z(),
        "scheme": esquema
    }

    # 7) Calcular checksum
    obj["checksum_hex"] = generar_checksum(obj, "checksum_hex")

    # 8) Guardar archivo
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, sort_keys=True, indent=2, ensure_ascii=False)

    establecer_permiso_solo_usuario(path)

    # 9) Limpiar datos sensibles de memoria
    _borrar_bytes(clave_derivada)
    _borrar_bytes(priv_bytes)
    try:
        del clave_derivada, priv_bytes
        gc.collect()
    except:
        pass

    return obj

# Lo siguiente carga un archivo keystore, valida su checksum y recupera la llave privada real descifrándola.

def cargar_keystore(path: str, passphrase: str):




    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)

    # Verificar checksum
    checksum_provisto = obj.get("checksum_hex")
    checksum_calc = generar_checksum(obj, "checksum_hex")

    if checksum_provisto != checksum_calc:
        raise ValueError("Checksum incorrecto: el archivo fue modificado.")

    if obj.get("kdf") != "Argon2id":
        raise NotImplementedError("Solo Argon2id está implementado aquí.")

    # Extraer parámetros
    kdfp = obj["kdf_params"]
    salt = de_base64(kdfp["salt_b64"])

    nonce = de_base64(obj["cipher_params"]["nonce_b64"])
    ciphertext = de_base64(obj["ciphertext_b64"])
    tag = de_base64(obj["tag_b64"])
    pub_bytes = de_base64(obj["pubkey_b64"])

    # Derivar la clave nuevamente
    clave = derivar_clave_argon2(
        passphrase,
        salt,
        time_cost=int(kdfp["time_cost"]),
        memory_cost_kib=int(kdfp["memory_cost_kib"]),
        parallelism=int(kdfp["parallelism"]),
        longitud=32
    )

    # Descifrar llave privada
    priv_bytes = descifrar_llave_privada(ciphertext, tag, clave, nonce)

    # Reconstruir objeto privado Ed25519
    priv = ed25519.Ed25519PrivateKey.from_private_bytes(priv_bytes)

    # Limpieza de memoria
    _borrar_bytes(clave)

    return priv, pub_bytes, obj


# Esta parte es para borrar elementos sensibles que puedan generarse en la RAM algo fancy xD


def _borrar_bytes(b: bytes):

    try:
        if isinstance(b, bytearray):
            for i in range(len(b)):
                b[i] = 0
        else:
            tmp = bytearray(b)
            for i in range(len(tmp)):
                tmp[i] = 0
            del tmp
    except:
        pass

    try:
        del b
        gc.collect()
    except:
        pass

