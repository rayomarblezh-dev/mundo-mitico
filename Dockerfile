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
RUN mongosh "mongodb://mongo:npMengYxzYkEtSATSPFyixaPDDBmZtGE@crossover.proxy.rlwy.net:24556" --eval "db.runCommand({ connectionStatus: 1 })"
# Limpia todas las colecciones relevantes de mundo_mitico (temporal)
RUN mongosh "mongodb://mongo:npMengYxzYkEtSATSPFyixaPDDBmZtGE@crossover.proxy.rlwy.net:24556" --eval "db.getCollection('mundo_mitico').deleteMany({})"
RUN mongosh "mongodb://mongo:npMengYxzYkEtSATSPFyixaPDDBmZtGE@crossover.proxy.rlwy.net:24556" --eval "db.getCollection('usuarios').deleteMany({})"
RUN mongosh "mongodb://mongo:npMengYxzYkEtSATSPFyixaPDDBmZtGE@crossover.proxy.rlwy.net:24556" --eval "db.getCollection('depositos').deleteMany({})"
RUN mongosh "mongodb://mongo:npMengYxzYkEtSATSPFyixaPDDBmZtGE@crossover.proxy.rlwy.net:24556" --eval "db.getCollection('creditos').deleteMany({})"

COPY . .
EXPOSE 8080
CMD ["python", "main.py"] 