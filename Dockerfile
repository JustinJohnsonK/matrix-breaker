# Dockerfile for Flask backend
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN apt-get update && apt-get install -y netcat-openbsd && pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x wait-for-it.sh
EXPOSE 5000
CMD ["./wait-for-it.sh", "db", "5432", "--", "python", "app/main.py"]
