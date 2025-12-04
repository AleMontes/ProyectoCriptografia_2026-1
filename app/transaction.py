import time
import json

class Transaction:
    def __init__(self, sender, receiver, value, nonce, gas_limit=21000, data_hex="", timestamp=None):
        """
        Inicializa una transacción 
        """

        if not sender or not receiver:
            raise ValueError("Sender y Receiver son obligatorios")
            
        self.sender = sender
        self.receiver = receiver
        self.value = str(value) 
        self.nonce = int(nonce)
        self.gas_limit = int(gas_limit)
        self.data_hex = data_hex
        
        if timestamp is None:
            self.timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        else:
            self.timestamp = timestamp

    def to_dict(self):
        """
        Convierte la transacción a un diccionario estándar de Python
        """
        
        return {
            "from_address": self.sender,
            "to": self.receiver,
            "value": str(self.value),
            "nonce": str(self.nonce),
            "gas_limit": str(self.gas_limit),
            "data_hex": self.data_hex,
            "timestamp": self.timestamp
        }