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
