from slowapi import Limiter
from slowapi.util import get_remote_address

# Por IP: evita que ni tú mismo lances 50 ataques por error en un loop,
# y frena fuerza bruta contra /api/auth/login.
limiter = Limiter(key_func=get_remote_address)
