# VectorRT

Plataforma web para lanzar ataques controlados (escaneo de puertos, fuerza bruta SSH, carga/DDoS pequeño) contra infraestructura **propia**, aislada en una red de laboratorio local.

> ⚠️ Este proyecto está en desarrollo siguiendo el [roadmap](roadmap.md). Todavía no hay código de aplicación en el repositorio.

## Uso responsable

Esta herramienta está diseñada **exclusivamente** para ejecutarse contra hosts de un laboratorio propio, aislado de red (sin salida a internet ni a redes de terceros). No está pensada ni autorizada para atacar infraestructura que no controles o sobre la que no tengas permiso explícito.

- Nunca apuntes esta plataforma a IPs o dominios que no sean de tu propio laboratorio.
- No expongas la plataforma en redes públicas sin autenticación.
- No commitees IPs de producción, credenciales del lab ni wordlists sensibles — usa `.env` / `.env.example`.

## Arquitectura

| Componente | Tecnología |
|---|---|
| Frontend | React + Vite + Tailwind |
| Backend | FastAPI + Uvicorn |
| Comunicación en vivo | WebSockets |
| Cola de jobs | asyncio.Queue o Celery + Redis |
| Base de datos | SQLite → PostgreSQL |
| Herramientas de ataque | nmap, hydra, hping3/siege |
| Infra de lab | Docker Compose / VirtualBox / Proxmox, red aislada |
| Defensa (opcional) | fail2ban, Suricata/Zeek |

```
VectorRT/
  frontend/    # React + Vite + Tailwind
  backend/     # FastAPI, servicios de ataque, modelos, rutas
  infra/       # IaC / scripts de la red de laboratorio
  docs/        # Topología de red, diagramas, notas
```

## Requisitos

- Un entorno de virtualización (Docker Compose, VirtualBox/VMware o Proxmox) para levantar la red de laboratorio aislada.
- Python 3.11+ y Node.js 18+.
- Herramientas de red instaladas en la máquina/VM atacante: `nmap`, `hydra`, `hping3` (o `siege`/`ab`).

## Puesta en marcha

### 1. Laboratorio

1. Crea una red virtual privada (ej. `10.10.10.0/24`) en modo *host-only*/*internal*, sin salida a internet.
2. Levanta las VMs/contenedores objetivo (SSH target, web target, multi-service target) con IP estática.
3. Valida manualmente cada herramienta de ataque contra los targets antes de integrarla en el backend.

Detalles completos de esta fase en el [roadmap](roadmap.md#fase-0--preparación-del-entorno-de-laboratorio).

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # configura la whitelist de targets y demás variables
uvicorn app.main:app --reload
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

El frontend se conecta al backend vía proxy de desarrollo (`vite.config.js`) y consume tanto la API REST como el WebSocket de streaming de resultados.

## Roadmap

El desarrollo está organizado en fases incrementales, cada una con un checklist propio:

0. **Preparación del entorno de laboratorio** — red aislada y VMs objetivo.
1. **Backend mínimo** — whitelist de targets y primer endpoint (escaneo de puertos).
2. **Frontend básico + tiempo real** — UI de selección de target y streaming por WebSocket.
3. **Módulos de ataque restantes + persistencia** — fuerza bruta SSH, carga/DDoS, base de datos, cola de jobs, histórico.
4. **Endurecimiento** — autenticación, validación de inputs, rate limiting, observabilidad, documentación.
5. **Blue Team (opcional)** — detección de los propios ataques (fail2ban, Suricata/Zeek) y reporte automático.

Ver el detalle completo en [roadmap.md](roadmap.md).

## Principios de seguridad del propio backend

- Todo endpoint valida el target contra una whitelist antes de ejecutar cualquier comando.
- Los comandos se ejecutan con `subprocess`/`asyncio.create_subprocess_exec` usando listas de argumentos, nunca `shell=True` con interpolación de strings del usuario.
- Los inputs se validan y sanitizan con Pydantic (IPs, duraciones acotadas, parámetros predefinidos).
- Límites duros en backend para los módulos de carga (duración y concurrencia máximas), independientes de lo que envíe el frontend.
