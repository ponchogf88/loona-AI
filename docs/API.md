# LOONA API

Contrato y estado documentado del runtime local que consume `hud/`. Base esperada: `http://127.0.0.1:8766`. Los endpoints de producto descritos abajo son los que el HUD usa para el briefing de mañana, clima, calendario y noticias.

## `GET /dash.html`

Shell visual de los dashboards de vida. URL completa: `http://127.0.0.1:8766/dash.html`. Se abre desde el botón **VIDA** del HUD.

- Presenta módulos de salud, finanzas, ejercicio, alimentación, calendarios y centro de mensajes.
- La UI usa la marca LOONA: void negro, oro escaso, estrellas sparse, tipografías Syne/Outfit y cards hairline.
- Es una shell de producto; las cifras actuales pueden ser placeholders y no deben citarse como saldos reales.
- El calendario se consume como datos/timeline, no como letter-grid.

Archivos de implementación (solo referencia, no cambios desde esta documentación): `hud/dash.html`, `hud/css/dash.css`, `hud/js/dash.js`.

### `/api/dash/*`

Claude dejó estos endpoints de estructura para la shell; no son datos personales reales hasta conectar sus fuentes:

- `GET /api/dash/health` — métricas de salud con `placeholder: true` cuando falta Apple Salud/CSV/entrada.
- `GET /api/dash/finance` — métricas financieras con `placeholder: true` cuando falta Notion/CSV.
- `GET /api/dash/exercise` — rutina diaria real del briefing; métricas de racha/sesiones/minutos siguen placeholder hasta existir un log.

Estado 2026-08-14 14:27 MTY: health, Cast, desktop snap y dispositivos tienen evidencia `200`. Eufy cuenta configurada (`account_configured:true`), pero `EUFY_RTSP_URL` está ausente; el snap Eufy sigue `501` y `pet/light` `NEED_HUMAN` por límite de librería.

### `GET /api/viva`

Endpoint de estado/presencia del sistema. Existe en el runtime según verificación de Grok; el contrato detallado queda pendiente de una captura de respuesta estable.

### `POST /api/pet`

Endpoint de interacción “pet” del HUD/presencia. Existe en el runtime según verificación de Grok; el payload y response exactos quedan pendientes de documentación con evidencia de contrato.

### Casa Apex

- Cast Nest Hub 2: `GET /api/devices` y `POST /api/cast/tts` verificados en Choza; prueba “amigo + pet”.
- Cast card: `POST /api/cast/card` acepta la tarjeta de estado visual y devuelve `200` cuando se publica en Choza. Verificado 2026-08-15 02:35 MTY con `card-20260815-023537.jpg` y clima 26° MTY.
- Eyes: `GET /api/eyes/status` reporta desktop OK. Eufy requiere configuración local y RTSP; Claude recibió Día 3 para luz + un frame.

## Convenciones

- Base URL: `http://127.0.0.1:8766` (o el puerto configurado en `config/loona.default.json`).
- `Content-Type: application/json` en requests y responses JSON.
- El runtime debe enlazar a `127.0.0.1` por defecto; no debe hacer port-forward.
- Las respuestas de contenido pueden incluir `speech`, `image` y `source`; el HUD decide cómo presentarlas.
- Los errores de validación usan HTTP `422` y esta forma exacta:

```json
{"ok": false, "error": {"code": "validation_error", "message": "...", "fields": {}}}
```

## `GET /api/health`

Response `200`:

```json
{"ok": true, "name": "LOONA"}
```

No requiere autenticación ni acceso a un provider.

## `GET /api/config`

Response `200`: el objeto completo de configuración, con la forma y restricciones de `config/loona.schema.json`. Debe ser compatible con `config/loona.default.json`; no debe incluir secretos.

## `PUT /api/config`

Request: el objeto completo de configuración JSON. El runtime valida contra `config/loona.schema.json`, rechaza propiedades desconocidas y no aplica cambios parciales.

Response `200`: el objeto completo validado y persistido.

Response `422`: error de validación en la forma de error definida arriba.

## `GET /api/knowledge`

Response `200`:

```json
{
  "ok": true,
  "documents": {
    "soul": {"path": "identity/SOUL.md", "content": "..."},
    "memory": {"path": "identity/MEMORY.md", "content": "..."}
  }
}
```

`content` es texto UTF-8. El endpoint solo sirve esos documentos dentro del workspace; nunca sirve `.env`, llavero, claves u otros secretos.

## `POST /api/chat`

Request:

```json
{"message": "texto del usuario"}
```

`message` es obligatorio, string no vacío, con máximo recomendado de 16.000 caracteres.

Response `200`:

```json
{"ok": true, "reply": "texto de LOONA", "provider": "deepseek"}
```

`provider` y `model` identifican la configuración efectiva; no contienen credenciales. Si no hay provider disponible, response `503`:

```json
{"ok": false, "error": {"code": "provider_unavailable", "message": "No hay provider disponible", "fields": {}}}
```

Antes de ejecutar tools, el middleware debe rechazar solicitudes para leer secretos (`.env`, llavero, API keys) o publicar en redes. El rechazo no llama al provider ni ejecuta la acción y usa `403` con `code` `guardrail_blocked`.

## `GET /api/briefing`

Briefing automático de inicio del día. No es un endpoint click-to-read: el HUD lo solicita al arrancar la sesión y puede reproducir el campo `speech`.

Response `200`:

```json
{
  "ok": true,
  "greeting": "Buenos días, Chuy.",
  "routine": [{"time": "08:00", "title": "...", "status": "upcoming"}],
  "weather": {"location": "Monterrey", "temperature_c": 24, "summary": "..."},
  "news": [{"title": "...", "source": "Xataka", "image": "https://...", "url": "https://..."}],
  "speech": {"text": "...", "voice": "Dalia", "provider": "edge-tts"}
}
```

`routine` es la rutina del día; `weather` resume MTY; `news` contiene noticias IA con imagen; `speech` es el texto y la voz neural que el HUD puede reproducir. El briefing no requiere que el usuario pulse “leer”.

## `GET /api/weather`

Clima de Monterrey obtenido de Open-Meteo.

Response `200`:

```json
{
  "ok": true,
  "location": "Monterrey",
  "provider": "open-meteo",
  "current": {"temperature_c": 24, "apparent_temperature_c": 25, "weather_code": 1, "wind_kmh": 12},
  "updated_at": "2026-08-12T..."
}
```

Las unidades expuestas al HUD son Celsius y km/h. No requiere una API key propia.

## `GET /api/calendar`

Calendario mensual con próximos eventos. El contrato no devuelve una cuadrícula de letras como interfaz de usuario; el HUD presenta timeline y lista de próximos eventos.

Response `200`:

```json
{
  "ok": true,
  "month": "2026-08",
  "events": [{"id": "...", "title": "...", "start": "2026-08-12T09:00:00-06:00", "end": "2026-08-12T10:00:00-06:00"}],
  "upcoming": [{"id": "...", "title": "...", "start": "2026-08-12T09:00:00-06:00", "relative": "en 20 min"}]
}
```

## `GET /api/news?topic=ai`

Feed de noticias sobre IA con imagen y fuente. El topic documentado para el briefing es `ai`.

Response `200`:

```json
{
  "ok": true,
  "topic": "ai",
  "items": [{"title": "...", "source": "Xataka", "image": "https://...", "url": "https://...", "published_at": "2026-08-12T..."}]
}
```

Fuentes esperadas: Xataka, El País y Wired. El HUD muestra las imágenes; si un artículo no tiene `image`, se omite del carrusel visual.

## Estado live reportado

- `GET /api/briefing`: verde — saludo, rutina, clima MTY, noticias IA y speech.
- `GET /api/weather`: verde — Open-Meteo Monterrey.
- `GET /api/calendar`: verde — mes + `upcoming`, presentado como timeline.
- `GET /api/news?topic=ai`: verde — feed con imágenes.
- HUD: morph de voz, TV solo imágenes y Pulse compacto.
- Dash: `/api/dash/health`, `/api/dash/finance` y `/api/dash/exercise` documentados como estructura honesta; no confundir placeholders con datos reales.

## Casa Apex: dispositivos y sentidos

El objetivo P0 es integrar hardware real sin mover el HUD a una función de dispositivo:

- **Nest Hub 2 = boca:** Cast verificado en Choza; reproduce audio TTS de LOONA y puede mostrar tarjeta de saludo/clima/estado.
- **Eufy Indoor Cam E30 T8417 = ojo:** devolverá un frame bajo demanda cuando Chuy pregunte “qué ves”; no se envía un stream cada 10 segundos.
- **HUD Apex = presencia:** busto, crew, SPEAKING, reloj y clima; el HUD coordina, Nest habla y Eufy mira.

Contrato Eufy pendiente de Claude:

```text
GET  /api/eyes/status
GET  /api/eyes/snap?src=desktop|eufy
```

`/api/eyes/status` ya reporta desktop OK; `/api/eyes/snap` y la integración Eufy siguen pendientes. Cast Nest no pertenece ya a esta lista pendiente.

### Eyes y luz Eufy — estado canónico 2026-08-14 14:27

- `GET /api/eyes/status`: desktop FaceTime + ffmpeg OK; Eufy `account_configured:true`, RTSP ausente.
- `GET /api/eyes/snap?src=eufy`: HTTP `501` mientras falte `EUFY_RTSP_URL`.
- `POST /api/pet/light`: `NEED_HUMAN` por límite de la librería, no por falta de cuenta.
- No se declara Eufy terminado: falta RTSP y el frame real.

Cast/devices/card ya están verificados: `GET /api/devices`, `POST /api/cast/tts` y `POST /api/cast/card` → 200 en Choza. Día 7 queda como loop voz + tarjeta en el mismo beat.

## Brand paths

La fuente visual canónica está en `brand/`:

| Recurso | Path | Uso |
|---|---|---|
| Mark | `brand/mark-crescent.jpg` | Media luna hairline + estrella |
| Wordmark | `brand/wordmark.jpg` | LOONA oro con tracking amplio |
| Lockup | `brand/lockup.jpg` | Luna + LOONA; lockup principal |
| App icon | `brand/app-icon.jpg` | Icono de aplicación |
| Hero | `brand/hero-space.jpg` | Landing y still del explainer |

Copias servidas por el HUD: `hud/brand/`. Tokens: void `#000000`/`#070B12`, oro `#E8D5A3`→`#F3D19A`, cobre/magenta para la cabeza, violeta `#C084FC` como acento de partícula. No usar verde menta ni llenar el fondo de estrellas.

## Stack explainer

El stack canónico y el guion viven en `docs/video/STACK_EXPLAINER.md` y `docs/video/GUION_EXPLAINER_240.md`.

- Duración objetivo: 2:40, 16 bloques de 10 segundos, formato 16:9.
- Pipeline: still/product reference → style key → narración ES-MX → clips `gemini_omni` → ensamblado `explainer_video`.
- Estilo: void negro, oro champagne, 5–8 estrellas, UI real de LOONA, cursor y microinteracciones de 200–500 ms.
- Transiciones: match cut, UI morph y mockup iMac/iPhone en los bloques definidos por el stack.
- Voz de prototipo: `edge-tts` Dalia; Higgsfield es la ruta prevista para generación/ensamble.

Estado: guion y stack documentados; el render sigue pendiente de créditos/autoridad del proveedor. Este documento no declara el explainer DONE.

En este turno el smoke-check desde shell no pudo conectar al proceso local; no se modificó `runtime/` para forzarlo.

## Estado de implementación

- [x] Contratos de briefing, weather, calendar y news documentados.
- [x] Estado visual reportado: morph de voz, TV imagen-only y Pulse compacto.
- [ ] Repetir smoke-check HTTP cuando el proceso local vuelva a escuchar en `127.0.0.1:8766`.
