# Disco iMac — inventario operativo

**Corte:** 2026-08-13 · **Fuente:** evidencia de Grok · **Equipo:** iMac Intel LOONA

## Estado crítico

- Contenedor APFS: **1,000 GB**.
- Data volume usado: **940.5 GB**.
- Libre aproximado: **~13 GB**.
- Diagnóstico: **12–13 GB libres es poco** para macOS, Chrome, modelos locales y operaciones de video. No instalar ni generar archivos grandes sin liberar espacio o confirmar destino.

## Medición disponible

| Ubicación/categoría | Tamaño | Nota |
|---|---:|---|
| VM / `sleepimage` | 13 GB | Memoria virtual/hibernación; no borrar a ciegas. |
| Chrome App Support | 9 GB | OptGuide weights 2.7 GB + cache 1.3 GB, resto no desglosado aquí. |
| AMDA `ghost_chrome` weights | 2.7 GB | Duplicado de pesos OptGuide; candidato a revisar, no borrar sin confirmar uso. |
| `Photos.sqlite` | 1.8 GB | Base de datos de Fotos. |
| Photo Booth | 3.4 GB | Medido; revisar contenido antes de cualquier limpieza. |
| JESUS GUTIERREZ PHOTOGRAPHY | 7.8 GB | Medido; no borrar. |
| iCloud Mobile Documents | 3.1 GB | Datos sincronizados; no borrar manualmente. |
| Ollama | 1.9 GB | Modelos/datos locales; revisar modelos antes de retirar. |
| Productos Digitales | 1.1 GB | Incluye un `.mov` de 800 MB. |
| Claude | 1.5 GB | Datos de aplicación. |
| Comet | 1.2 GB | Datos de aplicación. |
| Microsoft | 1.1 GB | Datos de aplicación. |

Estas cifras son categorías medidas, no una suma completa del disco. No convertir el espacio no explicado en una afirmación de “800 GB en una carpeta”.

## Búsqueda y límites

- No hay un archivo de usuario individual >8 GB identificado por Spotlight, aparte de las categorías medidas arriba.
- Timeouts durante la medición: `AMDA` completo, `GUTIERREZ CONSULTING`, `Containers`, `Desktop` y `Documents`.
- `DriveFS` no está instalado.
- El informe esperado de Claude en `/Users/imac/Desktop/STORAGE_SCAN_CLAUDE.md` **no existe todavía** en este corte. No se rellenan sus cifras faltantes.

## Duplicado prioritario

`Chrome App Support` contiene pesos OptGuide de 2.7 GB y `AMDA/ghost_chrome` contiene otros 2.7 GB descritos como duplicados. Próximo paso seguro: identificar propietario/proceso y confirmar si ambos se pueden regenerar; después proponer una limpieza reversible. No ejecutar borrado automático.

## Guardrails

- No borrar nada desde este inventario.
- No tocar Photos, iCloud, documentos personales, `Containers` o aplicaciones sin una decisión explícita de Chuy.
- Antes de liberar espacio: medir con `du`/Storage, registrar path exacto, verificar que no sea sincronizado ni activo y mover a papelera/backup según gate humano.
- El objetivo inmediato es recuperar margen operativo; no optimizar a costa de perder datos.

## Handoff

- Claude `w2:pB`: completar `/Users/imac/Desktop/STORAGE_SCAN_CLAUDE.md` con cifras o paths que hayan quedado en timeout.
- Codex: incorporar el informe solo cuando exista y distinguir medición de inferencia.
- Grok/Chuy: decidir qué cachés o pesos duplicados son recuperables.
