# Topología de red del laboratorio

Red interna Docker `vectorrt-lab`, subred `10.10.10.0/24`, sin salida a internet (`internal: true`).

| Host | IP | Rol | Servicios |
|---|---|---|---|
| ssh-target | 10.10.10.10 | SSH target | OpenSSH (usuario `labuser`, contraseña débil de prueba) |
| web-target | 10.10.10.11 | Web target | HTTP simple, puerto 8080 |
| multi-target | 10.10.10.12 | Multi-service target | FTP anónimo (21), Telnet con usuario débil (23), servicio custom (9000) |
| attacker | 10.10.10.20 | Máquina atacante (validación manual) | nmap, hydra, hping3, siege |
| backend | 10.10.10.30 | API VectorRT | FastAPI, publicado en el host como `localhost:8000`. Ejecuta nmap/hydra/hping3 contra el resto del lab |

Definido en [`infra/docker-compose.yml`](../infra/docker-compose.yml).

## Arquitectura

Todo el lab se construye desde `Dockerfile`s propios sobre imágenes multi-arch (`ubuntu:22.04`, `python:3.12-slim`, `kalilinux/kali-rolling`), por lo que funciona tanto en **arm64** (Apple Silicon, probado en MacBook Pro M5) como en **amd64**, sin cambios. No dependemos de imágenes precompiladas solo-amd64 (como `metasploitable2`), que fallan o van muy lentas bajo emulación en Apple Silicon — por eso el `multi-target` se construye a mano con `vsftpd` + `telnetd`/`xinetd` + un servicio custom en vez de usar esa imagen.

## Whitelist de targets (referencia para el backend)

```
10.10.10.10  ssh-target
10.10.10.11  web-target
10.10.10.12  multi-target
```

Esta lista es la que alimentará `is_target_allowed()` en el backend (Fase 1.2) — cualquier IP fuera de este rango debe ser rechazada por la API.
