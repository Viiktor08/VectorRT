# Red Team Platform — Roadmap de desarrollo desde 0

> **Alcance**: plataforma web para lanzar ataques controlados (escaneo de puertos, fuerza bruta SSH, carga/DDoS pequeño) contra infraestructura **propia**, aislada en red local. Este documento asume que todo el desarrollo y las pruebas ocurren dentro de un laboratorio que tú controlas por completo (VMs propias, red sin salida a hosts de terceros).

---

## Fase 0 — Preparación del entorno de laboratorio

### 0.1 Elegir la plataforma de virtualización
- [ ] Decidir entre: Docker Compose (más rápido, menos realista a nivel de red), VirtualBox/VMware (más realista, más pesado), o Proxmox (si tienes un servidor dedicado).
- [ ] Instalar la plataforma elegida en tu máquina anfitriona.
- [ ] Verificar que soporta redes tipo "host-only" o "bridge interno" (sin salida a internet salvo la que tú definas explícitamente).

### 0.2 Crear la red aislada
- [ ] Crear una red virtual privada, ej. `10.10.10.0/24`.
- [ ] Configurar el modo de red de las VMs/contenedores como *host-only* o *internal network* (no NAT hacia el exterior).
- [ ] Anotar en un documento de referencia el rango de IPs que vas a usar (esto luego será tu whitelist).

### 0.3 Levantar las máquinas objetivo
- [ ] **VM/contenedor 1 — "SSH target"**: Ubuntu/Debian mínimo, con `openssh-server` instalado. Crear un usuario de prueba (ej. `labuser`) con una contraseña débil a propósito (ej. `123456`) **solo para este entorno**.
- [ ] **VM/contenedor 2 — "Web target"**: levantar un servicio HTTP simple (Flask, Node/Express, o incluso `python -m http.server`) en el puerto 80 u 8080.
- [ ] **VM/contenedor 3 — "Multi-service target"**: máquina con varios puertos abiertos (ej. FTP, Telnet, un puerto custom) para probar el escaneo de puertos con resultados variados. Puedes usar imágenes deliberadamente vulnerables como *Metasploitable2* para ahorrar tiempo.
- [ ] Anotar las IPs fijas asignadas a cada VM (configurar IP estática, no DHCP, para que la whitelist sea estable).

### 0.4 Validar las herramientas de ataque manualmente
- [ ] Instalar en tu máquina de desarrollo (o en una VM "atacante" separada dentro de la misma red): `nmap`, `hydra`, `hping3` (o `siege`/`ab` como alternativa de carga).
- [ ] Ejecutar manualmente cada herramienta contra las VMs objetivo para confirmar que responden como esperas:
  - `nmap -sV -p 1-1000 10.10.10.11`
  - `hydra -l labuser -P wordlist.txt ssh://10.10.10.10`
  - `hping3 -S -p 80 --flood 10.10.10.12` (con mucho cuidado con el flag `--flood`, empieza sin él)
- [ ] Documentar los tiempos de ejecución aproximados de cada comando — te servirá luego para poner timeouts razonables en el backend.

### 0.5 Control de versiones del proyecto
- [ ] Crear el repositorio Git (`redteam-platform/`).
- [ ] Definir estructura inicial de carpetas: `/frontend`, `/backend`, `/infra` (IaC/scripts de la red de lab), `/docs`.
- [ ] Añadir un `.gitignore` cubriendo entornos virtuales, `node_modules`, credenciales, `.env`.
- [ ] **Nunca** commitear IPs reales de producción, contraseñas del lab ni wordlists con datos sensibles si el repo va a ser público — usa `.env` + `.env.example`.

---

## Fase 1 — Backend mínimo: un ataque, un endpoint

### 1.1 Configurar el proyecto backend
- [ ] Elegir framework: **FastAPI** (recomendado por soporte nativo de async + WebSockets).
- [ ] Crear entorno virtual Python (`python -m venv venv`) e instalar dependencias base: `fastapi`, `uvicorn`, `pydantic`, `python-dotenv`.
- [ ] Crear estructura inicial:
  ```
  backend/
    app/
      main.py
      config.py
      routers/
      services/
      models/
    requirements.txt
    .env.example
  ```

### 1.2 Definir la whitelist de objetivos
- [ ] Crear `config.py` con una lista/estructura de hosts permitidos (IP, nombre descriptivo, servicios esperados). Ejemplo: lista de diccionarios `{"ip": "10.10.10.10", "label": "SSH target"}`.
- [ ] Implementar una función `is_target_allowed(ip: str) -> bool` que se usará en **todos** los endpoints antes de ejecutar cualquier comando.
- [ ] Escribir un test unitario que verifique que una IP fuera de la whitelist es rechazada.

### 1.3 Primer endpoint: escaneo de puertos
- [ ] Crear `services/nmap_service.py` con una función `run_port_scan(target_ip: str) -> dict` que:
  - Valide el target contra la whitelist.
  - Construya el comando `nmap` con flags fijos (no permitir que el usuario inyecte flags libres).
  - Ejecute el comando con `asyncio.create_subprocess_exec` (no `shell=True`, para evitar inyección de comandos).
  - Capture stdout/stderr con timeout (ej. 60s).
  - Parsee la salida (puedes usar `python-nmap` en vez de parsear texto a mano).
- [ ] Crear el endpoint `POST /api/attacks/port-scan` en `routers/attacks.py` que reciba `{ "target_ip": "..." }` y devuelva el resultado.
- [ ] Probar con `curl` o Postman antes de tocar el frontend.

### 1.4 Logging básico
- [ ] Configurar `logging` de Python para registrar: timestamp, tipo de ataque, target, comando exacto ejecutado, resultado (éxito/error), duración.
- [ ] Decidir si los logs van a fichero, a stdout (para luego mandarlos a un colector), o directo a base de datos (lo haremos en Fase 3).

---

## Fase 2 — Frontend básico + comunicación en tiempo real

### 2.1 Setup del frontend
- [ ] Crear proyecto con Vite + React (`npm create vite@latest frontend -- --template react`).
- [ ] Instalar Tailwind CSS para estilos rápidos.
- [ ] Configurar proxy de desarrollo hacia el backend (`vite.config.js` → `server.proxy`).

### 2.2 Pantalla principal
- [ ] Crear componente `TargetSelector`: un `<select>` (no un input libre de texto) que liste **solo** las IPs de la whitelist que el backend expone vía `GET /api/targets`.
- [ ] Crear componente `AttackButtons`: tres botones — "Escaneo de puertos", "Fuerza bruta SSH", "Carga/DDoS pequeño" — deshabilitados hasta que haya un target seleccionado.
- [ ] Crear componente `ResultsPanel`: área donde se muestra el JSON/texto de resultado de cada ataque.

### 2.3 Conectar el primer botón al backend
- [ ] Implementar el `fetch`/`axios` call desde `AttackButtons` → `POST /api/attacks/port-scan`.
- [ ] Mostrar un estado de "Ejecutando..." mientras se espera respuesta.
- [ ] Renderizar el resultado (puertos abiertos, versión de servicio, etc.) en `ResultsPanel`.

### 2.4 WebSocket para streaming de output
- [ ] En el backend, añadir un endpoint WebSocket `/ws/attacks/{job_id}` que vaya emitiendo líneas de output del subproceso a medida que se generan (usando `process.stdout.readline()` en un loop async).
- [ ] En el frontend, conectar un `WebSocket` nativo o `socket.io-client` y volcar cada mensaje recibido en un componente tipo terminal (`<pre>` con auto-scroll).
- [ ] Probar el streaming con el escaneo de puertos, que suele tardar varios segundos — ideal para validar que el streaming funciona antes de añadir más módulos.

---

## Fase 3 — Añadir los módulos de ataque restantes + persistencia

### 3.1 Módulo de fuerza bruta SSH
- [ ] Crear `services/hydra_service.py` con `run_ssh_bruteforce(target_ip, username, wordlist_path)`.
- [ ] Restringir `username` y `wordlist_path` a valores predefinidos en el backend (no exponer un input libre de wordlist al frontend, para evitar que se usen wordlists gigantes o rutas arbitrarias).
- [ ] Endpoint `POST /api/attacks/ssh-bruteforce`.
- [ ] Botón correspondiente en el frontend, reusando el mismo patrón de streaming por WebSocket.

### 3.2 Módulo de carga/DDoS pequeño
- [ ] Decidir la herramienta: `hping3` (flood a nivel de paquete) vs `siege`/`ab` (carga HTTP, más "seguro" y fácil de acotar).
- [ ] Crear `services/load_service.py` con `run_load_test(target_ip, duration_seconds, concurrency)`.
- [ ] **Poner límites duros en el backend** (no confiar en el frontend): duración máxima (ej. 30s), concurrencia máxima (ej. 50 conexiones), para que nunca se pueda lanzar algo descontrolado por error.
- [ ] Endpoint `POST /api/attacks/load-test`.
- [ ] Botón en frontend con un pequeño formulario (duración, concurrencia) limitado por los mismos máximos que el backend.

### 3.3 Base de datos y modelo de datos
- [ ] Elegir DB: SQLite para desarrollo (simplicidad), PostgreSQL si quieres algo más "real".
- [ ] Definir modelo `AttackJob`: `id`, `attack_type`, `target_ip`, `params (JSON)`, `status`, `started_at`, `finished_at`, `raw_output`, `summary`.
- [ ] Integrar un ORM (SQLAlchemy) o un query builder ligero.
- [ ] Modificar los servicios de ataque para que, además de hacer streaming en vivo, guarden el job completo al finalizar.

### 3.4 Cola de jobs (evitar ataques concurrentes descontrolados)
- [ ] Decidir: `Celery + Redis` (robusto, más setup) o una cola in-memory simple con `asyncio.Queue` (suficiente para un proyecto personal).
- [ ] Implementar que solo se pueda correr **un ataque a la vez por target** (evita, por ejemplo, lanzar dos escaneos de puertos simultáneos contra la misma VM y confundir resultados).
- [ ] Mostrar en el frontend un estado "target ocupado" si ya hay un ataque en curso contra ese host.

### 3.5 Dashboard de histórico
- [ ] Endpoint `GET /api/attacks/history` con filtros por target y tipo de ataque.
- [ ] Vista `HistoryTable` en el frontend: tabla con fecha, tipo, target, estado, duración, y un botón "ver detalle" que muestre el output completo guardado.

---

## Fase 4 — Endurecimiento y buenas prácticas de la propia plataforma

### 4.1 Seguridad de la aplicación
- [ ] Añadir autenticación básica (usuario/contraseña o JWT) — aunque sea solo para ti, es buena práctica no dejar la plataforma abierta sin login.
- [ ] Revisar que **ningún** endpoint construya comandos de shell concatenando strings del usuario (usar siempre listas de argumentos con `subprocess`, nunca `shell=True` con interpolación).
- [ ] Sanitizar y validar con Pydantic todos los inputs (IPs con regex/`ipaddress` de Python, duraciones como enteros acotados, etc.).
- [ ] Rate limiting a nivel de API (ej. `slowapi`) para que ni tú mismo puedas lanzar 50 ataques por error en un loop.

### 4.2 Observabilidad
- [ ] Centralizar logs (aunque sea en un fichero rotado con `logging.handlers.RotatingFileHandler`).
- [ ] Añadir un endpoint `/health` para verificar que backend y conexión a DB están operativos.
- [ ] (Opcional) Exponer métricas básicas con `prometheus_client` (número de ataques lanzados, duración media, tasa de error).

### 4.3 Documentación
- [ ] README con: diagrama de arquitectura, instrucciones de instalación del lab, cómo levantar frontend+backend, y **una sección explícita de "Uso responsable"** dejando claro que la herramienta solo debe usarse contra infraestructura propia.
- [ ] Documentar en `/docs` la topología exacta de red del laboratorio (IPs, servicios por VM) para poder reconstruirlo si migras de máquina.

---

## Fase 5 (opcional/extensión) — Cerrar el círculo con Blue Team

### 5.1 Detección de los propios ataques
- [ ] Instalar `fail2ban` en la VM SSH target, configurado para banear tras N intentos fallidos — así puedes ver cómo tu módulo de fuerza bruta es detectado y bloqueado.
- [ ] Instalar Suricata o Zeek en la VM que hace de "gateway" de la red de lab, con reglas básicas de detección de escaneo de puertos y floods.
- [ ] Añadir un panel en el frontend que muestre, a modo de "resultado defensivo", si el ataque fue detectado/bloqueado (leyendo logs de `fail2ban`/Suricata).

### 5.2 Reporte automático
- [ ] Generar un informe (PDF o Markdown) al finalizar una sesión de pruebas, resumiendo qué ataques se lanzaron, contra qué targets, y qué detecciones se dispararon — un mini "pentest report" automatizado.

---

## Resumen de stack final

| Componente | Tecnología |
|---|---|
| Frontend | React + Vite + Tailwind |
| Backend | FastAPI + Uvicorn |
| Comunicación en vivo | WebSockets |
| Cola de jobs | asyncio.Queue o Celery+Redis |
| DB | SQLite → PostgreSQL |
| Herramientas de ataque | nmap, hydra, hping3/siege |
| Infra de lab | Docker Compose / VirtualBox / Proxmox, red aislada |
| Defensa (opcional) | fail2ban, Suricata/Zeek |

---

### Nota final
Cada fase está pensada para ser un incremento funcional por sí mismo (puedes hacer un commit/demo al final de cada fase). El orden importa: no tiene sentido construir el frontend antes de tener el lab funcionando y validado manualmente, porque necesitas saber exactamente qué formato de salida vas a parsear.
