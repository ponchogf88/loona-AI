# ROADMAP

v1 (hoy): single-operator, un Mac, un proceso FastAPI en `127.0.0.1`, sin auth,
protegido solo por `runtime/limits.py` (40 req/min/IP, 4 chats concurrentes).

## v2 — multi-seat (varios usuarios, un Mac o LAN)
- Auth mínima: token por dispositivo (header `Authorization`), no login social.
- Cuotas por usuario, no solo por IP (hoy dos personas en la misma red comparten límite).
- Sesiones/roles separados en `runtime/state/` (hoy es un solo config global).

## v3 — hosted (LOONA en un servidor, no en el iMac del dueño)
- Reemplazar `bind 127.0.0.1` por proxy TLS + auth real (OAuth/JWT) antes de exponer un puerto.
- Cola real para `/api/chat` (Redis/queue) en vez del semáforo en memoria de un proceso.
- Persistencia en base de datos para config/telemetría (hoy son archivos JSON locales).
- Rate limiting distribuido (hoy `limits.py` vive en memoria de un solo proceso).

No se hace ninguno de estos pasos sin decisión explícita del dueño — ver
`docs/GOVERNANCE.md` (acciones irreversibles / exponer red = ASK).
