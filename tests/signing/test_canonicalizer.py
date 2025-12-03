import sys
import os
import json
from app.canonicalizer import canonicalize

def test_canonicalize_orden():
    # Caso 1: Mismos datos, diferente orden en el diccionario
    data1 = {"b": "2", "a": "1"}
    data2 = {"a": "1", "b": "2"}
    
    # Deben generar EXACTAMENTE los mismos bytes
    assert canonicalize(data1) == canonicalize(data2)

def test_canonicalize_formato():
    # Caso 2: Verificar que no haya espacios y sea UTF-8
    data = {"cant": "100", "dest": "bob"}
    
    # json.dumps por defecto pone espacios (": ", ", "), canonicalize NO debe tenerlos
    expected = b'{"cant":"100","dest":"bob"}' 
    
    assert canonicalize(data) == expected

def test_tipos_de_datos():
    # Verificar que maneja caracteres especiales correctamente
    data = {"msg": "mañana", "val": "10"}
    res = canonicalize(data)
    assert b"msg" in res
    assert "mañana".encode('utf-8') in res