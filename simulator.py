from pathlib import Path
import json
import shutil
from verifier import verificar_firma, NonceStore

INBOX_DIR = Path("inbox") 
OUTBOX_DIR = Path("outbox") #
VERIFIED_DIR = Path("verified")
NONCES_FILE = Path("nonces.json")  


def asegurar_carpetas() -> None:
    for carpeta in [INBOX_DIR, OUTBOX_DIR, VERIFIED_DIR]:
        if not carpeta.exists():
            carpeta.mkdir()
            print(f"Creado {carpeta}")
        else:
            (f"Ya existe {asegurar_carpetas}")

def simular_entrega_desde_outbox() -> None:
    asegurar_carpetas()
    for archivo in OUTBOX_DIR.glob("*.json"):
        destino = INBOX_DIR / archivo.name
        shutil.move(archivo, destino)
        print(f"Entregado a inbox: {archivo.name}")

def procesar_inbox() -> None:
    asegurar_carpetas()
    nonce_store = NonceStore(NONCES_FILE)
    archivos = list(INBOX_DIR.glob("*.json"))
    if not archivos:
        print("No hay archivos para procesar en el inbox")
        return

    for archivo in archivos:
        try:
            contenido = archivo.read_text(encoding="utf-8")
            data = json.loads(contenido)
        except Exception as e:
            print(f"{archivo.name}: error al leer {e}")
            nuevo_nombre = INBOX_DIR / f"{archivo.stem}.badjson"
            archivo.rename(nuevo_nombre)
            continue

        resultado = verificar_firma(data, nonce_store)
        print(f"{archivo.name}: {resultado.as_dict()}")

        if resultado.valido:
            destino = VERIFIED_DIR / archivo.name
            shutil.move(archivo, destino)
        else: 
            nuevo_nombre = INBOX_DIR / f"{archivo.stem}.invalid.json"
            archivo.rename(nuevo_nombre)


if __name__ == "__main__":
    simular_entrega_desde_outbox()
    procesar_inbox()
