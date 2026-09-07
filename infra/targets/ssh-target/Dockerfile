# SSH target de laboratorio — 10.10.10.10
# Usuario y contraseña débiles A PROPÓSITO, solo para uso dentro del lab aislado.
FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-server && \
    mkdir /var/run/sshd && \
    useradd -m labuser && echo "labuser:123456" | chpasswd && \
    sed -i 's/#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
