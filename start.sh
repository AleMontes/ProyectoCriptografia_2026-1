#!/bin/bash

echo "============================================================"
echo "   Crypto Cold Wallet - Iniciando Servidor"
echo "============================================================"
echo ""

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no está instalado"
    echo "Por favor instala Python 3.8 o superior"
    exit 1
fi

echo "Verificando dependencias..."
echo ""

# Instalar dependencias si es necesario
pip3 install -q flask flask-cors 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Instalando dependencias..."
    pip3 install -r requirements.txt
fi

echo ""
echo "Iniciando servidor API..."
echo ""
echo "La interfaz web estará disponible en: http://localhost:5000"
echo "Presiona Ctrl+C para detener el servidor"
echo ""

# Iniciar el servidor
python3 api_server.py
