FROM python:3.11-slim

# Instalar Chromium y Chromium-Driver
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requerimientos e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Exponer el puerto de Render
EXPOSE 10000

# Comando para iniciar la API
CMD ["uvicorn", "autocheck:app", "--host", "0.0.0.0", "--port", "10000"]