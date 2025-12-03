@echo off
echo ============================================================
echo    Crypto Cold Wallet - Iniciando Servidor
echo ============================================================
echo.

REM Verificar que Python está instalado
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor instala Python 3.8 o superior
    pause
    exit /b 1
)

echo Verificando dependencias...
echo.

REM Instalar dependencias si es necesario
py -m pip install -q flask flask-cors 2>nul
if errorlevel 1 (
    echo Instalando dependencias...
    py -m pip install flask flask-cors cryptography argon2-cffi pycryptodome
)

echo.
echo Iniciando servidor API...
echo.
echo La interfaz web estara disponible en: http://localhost:5000
echo Presiona Ctrl+C para detener el servidor
echo.

REM Iniciar el servidor
py api_server.py

pause
