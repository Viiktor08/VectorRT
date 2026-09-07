FROM python:3.12-slim

# nmap, hydra e hping3 viven en el contenedor del backend: es quien ejecuta los
# ataques contra el resto del lab, no la máquina anfitriona.
RUN apt-get update && \
    apt-get install -y --no-install-recommends nmap hydra hping3 siege && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
