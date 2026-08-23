# Plan casa — LOONA tipo Apex (Nest Hub 2 + Eufy + escritorio)

**No Soltek.** Producto: el agente de Chuy. Referencias: Apex (mando), Zoey (cara), Jarvis (presencia).  
**Venta** del “robot personalizado” = después de que **esta casa** lo use 7 días. No al revés.

## Arquitectura de sentidos

Nest no reemplaza al HUD: es la **boca** remota. Eufy no se convierte en vigilancia continua: es el **ojo** bajo demanda. El HUD Apex sigue siendo la presencia y el coordinador.

- **Nest Hub 2 / boca:** Cast de TTS Dalia, tarjeta breve de saludo/clima/estado.
- **Eufy Indoor Cam E30 T8417 / ojo:** un frame cuando Chuy pregunta “qué ves” o en wake; RTSP/NAS solo si el menú de la cámara lo permite.
- **HUD Apex / presencia:** busto holográfico, crew, SPEAKING, reloj y clima; la cámara no debe dominar la escena.

Los contratos `/api/devices`, `/api/cast/tts` y `/api/eyes/*` quedan a cargo de Claude y se documentan en `docs/API.md` después de evidencia real. No se altera el calendario de siete días.

## Por qué el Nest Hub 2 no es chiflazón

Lo pagaste. Hoy es reloj. Puede ser **boca + cara secundaria**:

- Speaker: Cast de TTS (Dalia / la voz de LOONA).
- Pantalla: foto, estado SPEAKING, “buenos días”, clima. No el WebGL de 13k partículas (el Hub no lo corre bien).
- Controles: toques del Hub son limitados; la voz de LOONA manda. El Hub **reproduce**.

No inyectamos Gemini *dentro* de Google. Empujamos audio/imagen **hacia** el Hub.

## Ojos

| Ojo | Rol |
|---|---|
| **Eufy Indoor Cam E30 T8417** | Cuarto. Ya te sigue (tracking nativo). LOONA pide **1 frame** cuando preguntas “qué ves” o al wake. RTSP si el menú NAS existe. |
| **Cámara del escritorio** | Capture / espejo (ya está). Close-up. |

La Eufy “parece viva” porque **el hardware** te persigue. No hay que reinventar el pan-tilt el día 1.

## Días (esta casa, iMac + LAN)

| Día | DoD | Dueño | Gate humano |
|---|---|---|---|
| **1** | Descubrir Nest Hub 2 en la red. Cast de **un** MP3 de prueba. | Claude | Hub encendido, misma Wi‑Fi que el iMac |
| **2** | Cada `speak()` de LOONA también suena en el Hub. | Claude + HUD hook | — |
| **3** | Eufy: menú NAS/RTSP sí/no. Si sí: 1 frame en VLC + `/api/eyes/eufy`. | Claude + Chuy | App eufy, URL no en chat |
| **4–5** | HUD máximo Apex: busto, crew, SPEAKING, reloj. Cinemático, no web. | Agy | Cupo Agy |
| **6** | Hub muestra tarjeta (lockup + texto + clima) al hablar. | Claude | — |
| **7** | Loop: oyes → Gemini (cerebro actual) → voz Hub + 1 frame Eufy si pediste visión. | Grok verify | Mic / wake |

**Calendario realista:** **7 días** para “se oye en el Hub y te ve la Eufy cuando se lo pides”.  
**14 días** para que no se sienta demo (fallos Cast, stream Eufy que se cae, HUD pulido).  
**Vender el kit:** no antes de que **tú** lo uses una semana. Eso es mes 2, no día 8.

**Gate de venta:** siete días completos de uso doméstico observado; después se evalúan los 14 días de endurecimiento, pero ningún demo o screenshot cuenta como sustituto del uso en casa.

## Costo

Cast + Dalia = ~0 extra. Gemini por frase = lo de siempre.  
**No** mandar un frame a Gemini cada 10 s. Solo al wake o “qué ves”.

## Anti-patrones

- Mini-PC Windows primero (duplica SOUL).
- Bluetooth al Hub como plan A.
- API key en scripts.
- Mezclar Soltek.
- Declarar “ya es Apex” por un dock de botones.
