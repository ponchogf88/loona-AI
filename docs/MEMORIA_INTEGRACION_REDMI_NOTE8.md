# Memoria de Integración: Xiaomi Redmi Note 8 en Ecosistema LOONA

**Fecha:** 2026-08-16  
**Responsable:** Agy (`wB:p1`)  
**Estatus:** ACTIVO / OPTIMIZADO  

---

## 1. Resumen
Se integró el dispositivo físico **Xiaomi Redmi Note 8** (`ginkgo` / SN: `160305c5`) conectado por USB a la iMac del fundador. Se ejecutó un proceso de restauración de rendimiento, ajuste de zona horaria y debloat masivo para convertir el teléfono en un nodo de hardware secundario (sensor, puente y monitor de pruebas).

---

## 2. Diagnóstico & Problemas Resueltos
1. **Desfase Horario:** El equipo tenía zona horaria de Cuba, lo que bloqueaba la creación e inicio de sesión de cuentas por certificados SSL. Se configuró `America/Mexico_City` y sincronización automática.
2. **Reinicios por OOM:** La memoria RAM de 4GB estaba saturada por 27 apps de telemetría y bloatware. Se desactivaron/desinstalaron todos los paquetes pesados (MSA, Analytics, Daemons, Facebook, Google App, Telcel, apps duplicadas).
3. **Optimización de UI:** Se ajustaron animaciones a 0.5x, se configuró `stay_on_while_plugged_in=3` y se liberó más de 1.2 GB de RAM.
4. **Herramientas Instaladas:** `scrcpy 4.1` (Metal) y `android-platform-tools` (ADB) en la iMac.

---

## 3. Comandos de Operación
- **Lanzar Proyección:** `scrcpy --window-title="Redmi Note 8" --stay-awake`
- **Captura de Pantalla para IA:** `adb exec-out screencap -p > capture.png`
- **Mantenimiento:** `adb shell pm trim-caches 4096M && adb shell am kill-all`
