# Usamos una imagen oficial de Python ligera
FROM python:3.10-slim

# Definimos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de dependencias primero (para aprovechar el caché de Docker)
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el resto de tu código al contenedor
COPY . .

# HUGGING FACE REQUIERE EL PUERTO 7860 (No el 8000 que usa FastAPI por defecto)
EXPOSE 7860

# Comando para levantar el servidor
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]