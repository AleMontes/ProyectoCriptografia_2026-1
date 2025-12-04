"""
Módulo de compatibilidad para pysha3
Usa pycryptodome en su lugar
"""

from Crypto.Hash import keccak

def keccak_256(data=b''):
    """
    Crea un objeto keccak_256 compatible con pysha3
    """
    class Keccak256Wrapper:
        def __init__(self):
            self._hash = keccak.new(digest_bits=256)

        def update(self, data):
            self._hash.update(data)

        def digest(self):
            return self._hash.digest()

        def hexdigest(self):
            return self._hash.hexdigest()

    wrapper = Keccak256Wrapper()
    if data:
        wrapper.update(data)
    return wrapper
