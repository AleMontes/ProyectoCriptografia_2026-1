FROM python:3.10

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Creamos la carpeta de trabajo
WORKDIR /app

# Copiamos e instalamos dependencias
# (La imagen completa ya tiene compiladores, así que pip instalará
#  las librerías de criptografía sin quejarse).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente
COPY . .

# Comando por defecto
CMD ["/bin/bash"]