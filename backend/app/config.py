import ipaddress
from typing import TypedDict


class Target(TypedDict):
    ip: str
    label: str


# Whitelist de hosts del laboratorio (ver docs/topologia-lab.md).
# Cualquier IP fuera de esta lista debe ser rechazada por la API.
ALLOWED_TARGETS: list[Target] = [
    {"ip": "10.10.10.10", "label": "ssh-target"},
    {"ip": "10.10.10.11", "label": "web-target"},
    {"ip": "10.10.10.12", "label": "multi-target"},
]

_ALLOWED_IPS = {target["ip"] for target in ALLOWED_TARGETS}


def is_target_allowed(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return False
    return ip in _ALLOWED_IPS


# --- Fuerza bruta SSH (Fase 3.1) ---
# Usuario y wordlist fijos en el backend: el frontend nunca envía credenciales
# ni rutas de wordlist libres, para evitar wordlists gigantes o rutas arbitrarias.
LAB_SSH_USERNAME = "labuser"
LAB_SSH_PASSWORDS = ["123456", "labuser", "password", "admin", "letmein", "qwerty"]


# --- Carga / DDoS pequeño (Fase 3.2) ---
# Solo tiene sentido contra un target que hable HTTP; el resto de la whitelist
# (ssh-target, multi-target) no expone un servicio web al que aplicar siege.
class LoadTestTarget(TypedDict):
    port: int
    path: str


LOAD_TEST_TARGETS: dict[str, LoadTestTarget] = {
    "10.10.10.11": {"port": 8080, "path": "/"},  # web-target
}

# Límites duros en backend: el frontend nunca puede superarlos, ni por error.
MAX_LOAD_DURATION_SECONDS = 30
MAX_LOAD_CONCURRENCY = 50


def is_load_test_target_allowed(ip: str) -> bool:
    return ip in LOAD_TEST_TARGETS
