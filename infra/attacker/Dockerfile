# Contenedor atacante de laboratorio — 10.10.10.20
# Herramientas de validación manual (Fase 0.4): nmap, hydra, hping3, siege.
FROM kalilinux/kali-rolling

RUN apt-get update && \
    apt-get install -y --no-install-recommends nmap hydra hping3 siege && \
    rm -rf /var/lib/apt/lists/*

CMD ["bash"]
