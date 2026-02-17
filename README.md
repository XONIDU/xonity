# XONITY - Monitor con ESP32

Sistema de monitoreo con sensor de movimiento que envía alertas por correo y registra eventos en Excel.

## ⚡ Funcionamiento
- **ESP32** con sensor PIR detecta movimiento y envía datos al servidor cada 5 segundos (ping)
- **Servidor Flask** recibe datos, muestra interfaz web y envía alertas por correo
- **Alertas automáticas** ante movimiento, desconexión o reconexión del ESP32
- **Registro en Excel** de todos los eventos con fecha y hora

## 📦 Archivos incluidos
- `start.py` - Servidor web en Flask
- `xonity.ino` - Código para programar el ESP32
- `templates/index.html` - Interfaz web para monitoreo
- `casa1.xlsx` - Registro automático de eventos

## 🔧 Configuración rápida

### 1. Servidor (PC/Raspberry)
```bash
# Instalar dependencias
pip install flask pandas openpyxl

# Ejecutar servidor
python start.py

# Al iniciar te pedirá:
# 📧 Tu Gmail - para enviar alertas
# 🔑 Token de app (16 dígitos) - de Gmail
# 📨 Correo destino - quien recibe las alertas
```

### 2. ESP32 - Configurar en `xonity.ino`
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

## 🔌 Conexiones del sensor PIR
| Sensor PIR | ESP32    |
|------------|----------|
| VCC        | 3.3V     |
| GND        | GND      |
| OUT        | GPIO 4   |

## 🌐 Acceso a la interfaz web
- **Local:** `http://localhost:5000` o `http://IP-DEL-SERVIDOR:5000`
- **Remoto:** Usando Cloudflare Tunnel (gratis) - ideal para monitorear desde cualquier lugar
- La web muestra: estado de conexión, última vez con movimiento, último ping recibido

## 📧 Tipos de alertas por correo
- 🚨 **Movimiento detectado** - cuando el sensor se activa
- ⚠️ **ESP32 Desconectado** - si no recibe ping por 15 segundos
- 🔄 **ESP32 Reconectado** - cuando vuelve a conectarse
- *Cooldown de 5 minutos para evitar spam de correos*

## 📊 Registro automático
Todo se guarda en `casa1.xlsx`:
- Movimientos detectados con fecha y hora
- Conexiones y desconexiones del ESP32
- Historial completo para llevar control

## 🎯 Para qué usarlo
- Monitoreo de entrada principal
- Alarma casera económica
- Control de mascotas o adultos mayores
- Automatización del hogar
---
**Contacto:** xonidu@gmail.com  
**Creador:** Darian Alberto Camacho Salas  
**Tecnologías:** Python, Flask, ESP32, Sensor PIR, Excel, Cloudflare Tunnel
