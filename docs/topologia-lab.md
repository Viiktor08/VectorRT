# Topología de red del laboratorio

Red interna Docker `vectorrt-lab`, subred `10.10.10.0/24`, sin salida a internet (`internal: true`).

| Host | IP | Rol | Servicios |
|---|---|---|---|
| ssh-target | 10.10.10.10 | SSH target | OpenSSH (usuario `labuser`, contraseña débil de prueba) |
| web-target | 10.10.10.11 | Web target | HTTP simple, puerto 8080 |
| multi-target | 10.10.10.12 | Multi-service target | FTP anónimo (21), Telnet con usuario débil (23), servicio custom (9000) |
| attacker | 10.10.10.20 | Máquina atacante | nmap, hydra, hping3, siege |

Definido en [`infra/docker-compose.yml`](../infra/docker-compose.yml).

## Whitelist de targets (referencia para el backend)

```
10.10.10.10  ssh-target
10.10.10.11  web-target
10.10.10.12  multi-target
```

Esta lista es la que alimentará `is_target_allowed()` en el backend (Fase 1.2) — cualquier IP fuera de este rango debe ser rechazada por la API.
