# XONITY - Monitor con ESP32
**Darian Alberto Camacho Salas**

Sistema de monitoreo con sensor de movimiento que envía alertas por correo y registra eventos en Excel.

---

## ⚡ Funcionamiento
- **ESP32** con sensor PIR detecta movimiento y envía datos al servidor cada 5 segundos (ping)
- **Servidor Flask** recibe datos, muestra interfaz web y envía alertas por correo
- **Alertas automáticas** ante movimiento, desconexión o reconexión del ESP32
- **Registro en Excel** de todos los eventos con fecha y hora

---

## 📦 Archivos incluidos
| Archivo | Descripción |
|---------|-------------|
| `start.py` | Servidor web en Flask |
| `esp32.ino` | Código para programar el ESP32 |
| `templates/index.html` | Interfaz web para monitoreo |
| `casa1.xlsx` | Registro automático de eventos (se genera solo) |
| `diagrama.pdf` | Diagrama de conexiones |
| `requisitos.txt` | Dependencias de Python |
| `README.md` | Este archivo |

---

## 🔧 Configuración rápida

### 1. Servidor (PC, Raspberry Pi, o cualquier equipo)

```bash
# Instalar dependencias
pip install -r requisitos.txt

# O instalación manual
pip install flask pandas openpyxl qrcode

# Ejecutar servidor
python start.py
```

**Al iniciar te pedirá:**
- 📧 **Tu Gmail** - cuenta para enviar alertas
- 🔑 **Token de app (16 dígitos)** - desde https://myaccount.google.com/apppasswords
- 📨 **Correo destino** - quien recibe las alertas

### 2. ESP32 - Configurar en `esp32.ino`

```cpp
// ===== CONFIGURACIÓN WIFI =====
#define WIFI_SSID "TU_RED_WIFI"
#define WIFI_PASS "TU_CONTRASEÑA"

// ===== CONFIGURACIÓN DEL SERVIDOR =====
// Opción 1: ACCESO REMOTO con Cloudflare Tunnel (GRATIS)
// Descarga cloudflared desde cloudflare.com
// Ejecuta: cloudflared tunnel --url http://localhost:5000
// Te dará una URL tipo: https://ejemplo.trycloudflare.com
#define SERVER_HOST "ejemplo.trycloudflare.com"
#define SERVER_PORT 443
#define USE_HTTPS true

// Opción 2: RED LOCAL (para pruebas)
// #define SERVER_HOST "192.168.1.84"  // IP de tu PC
// #define SERVER_PORT 5000
// #define USE_HTTPS false

// ===== PIN DEL SENSOR =====
#define IR_SENSOR_PIN 4  // GPIO4 conectado al sensor PIR
```

### 3. Programar ESP32
1. Abre `esp32.ino` en Arduino IDE
2. Selecciona placa: "ESP32 Dev Module"
3. Conecta el ESP32 por USB
4. Sube el código

---

## 🔌 Conexiones del sensor PIR

| Sensor PIR | ESP32    |
|------------|----------|
| VCC        | 3.3V     |
| GND        | GND      |
| OUT        | GPIO 4   |

```
[PIR] VCC ──── 3.3V [ESP32]
[PIR] GND ──── GND  [ESP32]
[PIR] OUT ──── GPIO4 [ESP32]
```

---

## 🌐 Interfaz web

- **Local:** `http://localhost:5000` o `http://IP-DEL-SERVIDOR:5000`
- **Remoto:** URL de Cloudflare Tunnel

La web muestra en tiempo real:
- ✅ Estado de conexión del ESP32
- 🚶 Último movimiento detectado
- ⏱️ Último ping recibido
- ⏰ Hora del servidor

---

## 📧 Tipos de alertas por correo

| Evento | Asunto | Cooldown |
|--------|--------|----------|
| 🚨 Movimiento | "🚨 Movimiento detectado" | 10 seg (ESP32) |
| ⚠️ Desconexión | "⚠️ ESP32 Desconectado" | 5 minutos |
| 🔄 Reconexión | "🔄 ESP32 Reconectado" | 5 minutos |

*Cooldown evita spam de correos en desconexiones repetitivas*

---

## 📊 Registro automático

Todo se guarda en `casa1.xlsx` con formato:

| Tipo | Estado | Hora |
|------|--------|------|
| Movimiento | Detectado | 2026-02-21 14:32:15 |
| Conexión | Desconectado | 2026-02-21 16:45:22 |
| Conexión | Reconectado | 2026-02-21 16:45:30 |

---

## 🚀 Acceso remoto con Cloudflare Tunnel

### Instalación:
```bash
# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Ejecutar túnel
cloudflared tunnel --url http://localhost:5000
```

### Salida:
```
Your quick Tunnel has been created! Visit it at:
https://abc123.trycloudflare.com
```

Usa esta URL en el ESP32 y para acceso web remoto.

---

## 📱 Código QR

Al iniciar el servidor, se muestra un código QR con información de contacto y repositorio. ¡Escanéalo con tu móvil!

---

## 🎯 Aplicaciones

- 🏠 **Monitoreo de entrada principal**
- 🔐 **Alarma casera económica** (sin cuotas mensuales)
- 🐕 **Control de mascotas** (detectar movimiento cuando no hay nadie)
- 👴 **Monitoreo de adultos mayores** (alertas de actividad)
- 🤖 **Automatización del hogar** (base para sistemas más complejos)

---

## 📋 Requisitos del sistema

### Servidor:
- Python 3.6 o superior
- 512 MB RAM mínimo (87 MB usado)
- Cualquier SO: Windows, Linux, macOS, Raspberry Pi

### Hardware:
- ESP32 (cualquier modelo)
- Sensor PIR HC-SR501
- Cables jumper

---

## 🔧 Solución de problemas

| Problema | Posible solución |
|----------|------------------|
| ESP32 no se conecta | Verificar WiFi y credenciales |
| No llegan correos | Usar token de app (no contraseña normal) |
| Servidor no inicia | Instalar dependencias faltantes |
| QR no se ve | Terminal debe soportar caracteres UTF-8 |

---

## 📞 Contacto

- **Email:** xonidu@gmail.com
- **Repositorio:** https://github.com/XONIDU/xonity
- **Creador:** Darian Alberto Camacho Salas
- **Institución:** FESC-UNAM

---

**XONITY v1.0** - Febrero 2026  
*"Tecnología accesible para seguridad residencial"*
