FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Instala dependencias necesarias para mongosh
RUN apt-get update && apt-get install -y wget gnupg

# Instala mongosh
RUN wget -qO - https://pgp.mongodb.com/server-6.0.asc | apt-key add - \
    && echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list \
    && apt-get update \
    && apt-get install -y mongodb-mongosh

# Prueba la conexión a MongoDB
RUN mongosh "mongodb://mongo:PzIAIxpsrfvHQmmXESbaCkAyPPTwdWcf@tramway.proxy.rlwy.net:26295" --eval "db.runCommand({ connectionStatus: 1 })"

COPY . .
EXPOSE 8080
CMD ["python", "main.py"] 