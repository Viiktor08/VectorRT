# VectorRT — Mejoras futuras y escalabilidad

Brainstorm exhaustivo de todo lo que se podría añadir o mejorar a partir del estado actual (Fases 0-4 completas). No es un compromiso ni una prioridad — es un catálogo de opciones para elegir cuando se quiera seguir creciendo el proyecto.

---

## 1. Escalabilidad de la infraestructura del backend

- **Sustituir el lock en memoria (`asyncio.Lock`) por Redis** (`redlock`/`redis-py`) para que "un ataque a la vez por target" siga funcionando si se escala a varios workers/réplicas.
- **Sustituir el rate limiter en memoria de `slowapi` por su backend de Redis** — el limiter actual pierde el estado al reiniciar y no se comparte entre procesos.
- **Cola de jobs real** (Celery + Redis/RabbitMQ, o alternativas más ligeras como RQ o Arq) en vez de ejecutar el ataque en el propio proceso async del request — permite reintentos, prioridades, y desacoplar el backend web de la ejecución de ataques.
- **Múltiples workers de Uvicorn/Gunicorn** para aprovechar más CPU — hoy en día correr con `--workers > 1` rompería el lock y el rate limiter (ver sección de fallos).
- **Migrar SQLite → PostgreSQL** (ya apuntado en el roadmap original) para soportar escrituras concurrentes reales sin bloqueos de fichero.
- **Activar `PRAGMA journal_mode=WAL` en SQLite** como mejora intermedia de bajo esfuerzo antes de migrar a Postgres.
- **Particionado/archivado del histórico**: mover jobs antiguos a una tabla/almacén "frío" (o simplemente purgar `raw_output` de jobs viejos) para que la tabla `attack_jobs` no crezca sin límite.
- **Límite de tamaño de output**: truncar o paginar la salida de un ataque (líneas y bytes) tanto en memoria como en DB — evita que un ataque "ruidoso" (como el `siege` sin `-q`/`-j` que nos pasó durante el desarrollo) tumbe memoria del backend o el navegador.
- **Backpressure en el WebSocket**: agrupar líneas en lotes en vez de un mensaje JSON por línea si el volumen de output crece.
- **Reconexión automática del WebSocket** en el frontend si se cae la conexión a mitad de un ataque largo.
- **Graceful shutdown**: capturar `SIGTERM` para terminar limpiamente los ataques en curso (matar el subproceso, marcar el job como "cancelado" en vez de dejarlo eternamente en "running") al hacer `docker compose down` o un despliegue.
- **Readiness/liveness probes separados** (`/health/live`, `/health/ready`) si esto llega a correr en Kubernetes.
- **Autoscaling de targets efímeros**: en vez de 3 targets fijos siempre encendidos, poder pedir "dame un target SSH nuevo" y que se levante un contenedor on-demand con Docker API/Testcontainers, y se destruya al terminar la sesión.

## 2. Multiusuario, roles y auditoría

- **Multiusuario real** con tabla de usuarios en DB (hoy es una única cuenta por variables de entorno).
- **Roles/RBAC**: p.ej. "solo lectura" (ve histórico) vs "operador" (puede lanzar ataques) vs "admin" (gestiona targets/usuarios).
- **Permisos por target**: que un usuario solo pueda atacar ciertos hosts de la whitelist.
- **Auditoría**: quién lanzó cada ataque (hoy el job no guarda usuario, solo el resultado), con IP de origen y user-agent.
- **SSO/OAuth2** (GitHub/Google/OIDC genérico) si el proyecto se comparte con más gente, en vez de usuario/contraseña propios.
- **2FA/TOTP** para la cuenta de login.
- **Refresh tokens de vida corta + access tokens** en vez de un JWT único de 8h, con revocación server-side (hoy "cerrar sesión" es solo borrar el token en el navegador; el token sigue siendo válido hasta que caduca).
- **Notificaciones**: email/Slack/Discord webhook cuando termina un ataque largo o cuando se detecta desde el lado Blue Team (Fase 5).

## 3. Nuevos módulos de ataque

- **Escaneo web**: Nikto, `gobuster`/`dirb` (fuzzing de directorios), `sqlmap` contra un target con una app vulnerable de verdad.
- **Escáner de vulnerabilidades**: integración con OpenVAS/Greenbone o Nessus (si se tiene licencia) para CVEs reales, no solo banner grabbing.
- **Ataques a Active Directory** con un lab de AD (Impacket: `secretsdump`, `GetUserSPNs`, Kerberoasting) — mucho más realista que SSH+Telnet+FTP.
- **Simulación de phishing** (envío de correos de prueba contra un servidor SMTP del propio lab, tipo GoPhish).
- **Ataques inalámbricos** (si se añade una interfaz WiFi dedicada al lab — mucho más complejo de dockerizar, normalmente requiere hardware/VM real).
- **Post-explotación simulada**: tras un "compromiso" (p.ej. tras el SSH bruteforce exitoso), lanzar automáticamente una fase de post-explotación de juguete (listar usuarios, procesos) en el target, para enseñar la cadena completa.
- **MITM/ARP spoofing educativo** dentro del lab aislado (con `ettercap`/`bettercap`), como módulo opcional muy vigilado.
- **Password spraying** (variante de fuerza bruta con más usuarios y menos contraseñas) además del bruteforce actual usuario-fijo.
- **Enumeración SMB/SNMP** contra el `multi-target` si se le añaden esos servicios.
- **Fuzzing de la API/servicio custom** del `multi-target` (puerto 9000) con una herramienta tipo `radamsa` o similar, como ejercicio de fuzzing básico.

## 4. Reporting y analítica

- **Exportar informe en PDF/Markdown** al final de una sesión (ya está en el roadmap como Fase 5.2) — resumen de ataques, targets, hallazgos.
- **Mapeo a MITRE ATT&CK**: etiquetar cada módulo de ataque con su técnica ATT&CK correspondiente (T1046 Network Service Discovery, T1110 Brute Force, T1498 Network DoS...) para que el histórico sea "profesional".
- **Dashboard con gráficas**: ataques por tipo/target a lo largo del tiempo, tasa de éxito, tiempos medios (con la skill de dataviz, por ejemplo).
- **Diff entre dos escaneos de puertos** del mismo target (qué puerto se abrió/cerró entre dos fechas).
- **Export CSV/JSON** del histórico completo o filtrado.
- **Integración con herramientas de gestión de pentest** (Dradis, Faraday, PlexTrac) vía su API, para que VectorRT alimente un informe más grande.
- **Búsqueda y filtros avanzados en el histórico** (por rango de fechas, por texto en el output, por estado) — hoy solo hay filtro por target/tipo y un límite fijo de 100 resultados sin paginación real.

## 5. Blue Team / detección (extensión de la Fase 5 opcional)

- **SIEM real**: Wazuh o el stack ELK/Loki+Grafana recibiendo los logs de `fail2ban`/Suricata en vez de leerlos "a mano".
- **Alertas en tiempo real** (webhook a Slack/Discord/Telegram) cuando una detección salta durante un ataque.
- **Honeypots** adicionales en la red del lab para ver qué dispara ruido de fondo frente a ataques dirigidos.
- **Scoring de sigilo**: puntuar cada ataque lanzado según si fue detectado o no, y con qué retraso.
- **Réplica de un SOC en miniatura**: un dashboard "vista defensor" separado del "vista atacante".

## 6. Orquestación e Infraestructura como Código del lab

- **Terraform/Ansible/Vagrant** para levantar el lab también en VirtualBox/Proxmox/una nube privada, no solo Docker Compose — recuperar la opción original del roadmap para quien no esté en Apple Silicon o quiera más realismo de red.
- **Topologías de red configurables**: en vez de 3 targets fijos, generar la topología desde un fichero YAML (número de hosts, servicios, vulnerabilidades) — más variedad para practicar.
- **Snapshot/reset del lab con un botón**: volver todos los targets a su estado inicial sin `docker compose down/up` manual (interesante para sesiones de formación con varios alumnos).
- **Soporte GNS3/EVE-NG** para topologías de red L2/L3 más realistas (routers, VLANs, firewalls de verdad) en vez de una única red plana Docker.
- **Multi-lab**: poder tener varias instancias de laboratorio aisladas entre sí (por alumno/equipo) desde el mismo backend.

## 7. Observabilidad y DevOps

- **Métricas Prometheus** (ya contemplado como opcional en la Fase 4): número de ataques, duración media, tasa de error, latencia de la API — con dashboard Grafana.
- **Tracing distribuido** (OpenTelemetry) si la arquitectura crece a varios servicios.
- **Centralizar logs** en Loki/ELK en vez de solo un fichero rotado local.
- **CI/CD con GitHub Actions**: lint + tests backend (pytest) + build frontend en cada push/PR; hoy no hay ningún pipeline y los tests solo se ejecutan a mano.
- **Pre-commit hooks** (ruff/black para Python, eslint/prettier para JS) para que el estilo no dependa de acordarse de ejecutarlo.
- **Escaneo automático de dependencias**: `pip-audit`/`npm audit`/Dependabot o Renovate, y `trivy`/`grype` sobre las imágenes Docker del lab y del backend.
- **Build y publicación de imágenes** a un registry (GHCR/Docker Hub) versionadas, en vez de construir siempre en local.
- **Devcontainer** (`.devcontainer/`) para que cualquiera pueda abrir el repo en VS Code y tener el entorno listo sin instalar nada a mano.
- **Makefile/justfile** con atajos (`make lab-up`, `make test`, `make fmt`) para no tener que recordar los comandos largos de `docker compose`.

## 8. Frontend / experiencia de usuario

- **Terminal con color real** (xterm.js) en vez de `<pre>` texto plano, para que la salida de herramientas con color (si se reactivara) se vea como en una terminal de verdad.
- **Tema claro/oscuro** conmutable (hoy está fijo en oscuro).
- **Diseño responsive/móvil** — hoy está pensado para escritorio.
- **Paginación real del histórico** en vez de un límite fijo de 100 filas.
- **Favoritos/etiquetas** sobre targets o sobre entradas del histórico.
- **Notificación del navegador o sonido** cuando termina un ataque largo (útil si cambias de pestaña mientras corre un `load-test` de 30s).
- **Comparar dos jobs del histórico** lado a lado.
- **Cliente TypeScript autogenerado** desde el esquema OpenAPI de FastAPI (`openapi-typescript` o similar), para que frontend y backend no puedan desincronizarse en los tipos de request/response.
- **PWA instalable** si se usa mucho desde el navegador como una app aparte.

## 9. Seguridad de la propia plataforma (mejoras, no fallos — ver también el listado de fallos que pediste aparte)

- **Hash de contraseña con bcrypt/argon2** en vez de comparación en texto plano contra una variable de entorno.
- **Gestor de secretos** (Vault, SOPS, `.env` cifrado, o como mínimo Docker secrets) en vez de variables de entorno planas.
- **Rotación de `VECTORRT_SECRET_KEY`** con invalidación de tokens antiguos.
- **Cabeceras de seguridad HTTP** (CSP, `X-Content-Type-Options`, `Referrer-Policy`, etc.) vía middleware.
- **HTTPS local con `mkcert`** para practicar TLS incluso en el entorno de desarrollo.
- **Validación de `Origin` en el WebSocket** para mitigar Cross-Site WebSocket Hijacking si esto llega a exponerse más allá de `localhost`.
- **SBOM** (Software Bill of Materials) generado en CI para las imágenes del backend.

## 10. Testing

- **Tests de integración HTTP** con `httpx.AsyncClient`/`TestClient` de FastAPI contra los endpoints reales (login, whitelist, rate limiting) — hoy los 13 tests existentes son todos unitarios sobre módulos aislados (`config`, `auth`, `job_queue`), no hay ninguno que golpee un router HTTP de verdad, aunque `httpx` ya está en `requirements-dev.txt` sin usarse.
- **Tests E2E con Playwright integrados en el repo** (hoy las pruebas de navegador de esta conversación fueron scripts sueltos en un scratchpad, no quedaron como suite reutilizable).
- **Tests de carga del propio backend** (Locust/k6) — probar cómo aguanta VectorRT mismo bajo uso intensivo, no solo los targets del lab.
- **Cobertura de código** (`pytest-cov`) con un umbral mínimo exigido en CI.
- **Contract testing** entre frontend y backend basado en el esquema OpenAPI.

## 11. Nuevos targets / variedad del lab

- **Target con vulnerabilidad web real** (DVWA, OWASP Juice Shop) para practicar SQLi/XSS/etc., no solo servicios de red.
- **Target con base de datos expuesta** (MySQL/Mongo con auth débil) para un módulo de ataque nuevo.
- **Target Windows/AD** (más pesado, probablemente fuera de Docker — VM dedicada) para practicar el mundo Windows.
- **Generación aleatoria de topología** en cada `docker compose up` (qué puertos están abiertos, qué credenciales son débiles) para que no te aprendas el lab de memoria.

## 12. Empaquetado y distribución

- **Plantilla reutilizable**: convertir el repo en un "starter kit" que otros puedan clonar y adaptar para su propio lab de prácticas.
- **Imagen "todo en uno"** (docker-in-docker o similar) para repartir el lab completo a estudiantes en un único `docker run`.
- **Helm chart** si algún día se quiere correr sobre Kubernetes (probablemente overkill para este proyecto, pero es una opción).
- **Versionado semántico + changelog automático** (Conventional Commits + `semantic-release`).

---

### Cómo priorizar esto

La lista de arriba es deliberadamente exhaustiva y no todo tiene sentido para un proyecto personal de laboratorio. Si en algún momento se quiere avanzar, lo más rentable dado el estado actual sería probablemente, en este orden: (1) tests de integración HTTP + CI básico, (2) Redis para lock/rate-limit si se piensa correr con varios workers, (3) mapeo MITRE ATT&CK + informe exportable (cierra el círculo con la Fase 5), y (4) Postgres + WAL si el histórico empieza a crecer de verdad.
