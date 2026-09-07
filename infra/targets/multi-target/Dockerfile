# Multi-service target de laboratorio — 10.10.10.12
# Varios puertos abiertos para probar el escaneo de puertos con resultados variados.
# Construido nativo (sin depender de imágenes amd64-only tipo Metasploitable2,
# que no tienen build arm64 y fallan/van lentas bajo emulación en Apple Silicon).
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        vsftpd \
        telnetd \
        xinetd \
        update-inetd \
        python3 && \
    rm -rf /var/lib/apt/lists/*

# FTP anónimo de prueba, solo para el lab
RUN sed -i 's/anonymous_enable=NO/anonymous_enable=YES/' /etc/vsftpd.conf

# El paquete telnetd registra el servicio en /etc/inetd.conf (formato clásico),
# pero usamos xinetd, así que escribimos nosotros el fichero de servicio.
COPY xinetd-telnet.conf /etc/xinetd.d/telnet

# Usuario débil para el telnet de prueba
RUN useradd -m labuser && echo "labuser:123456" | chpasswd

COPY custom_service.py /opt/custom_service.py
COPY entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh

EXPOSE 21 23 9000
CMD ["/opt/entrypoint.sh"]
