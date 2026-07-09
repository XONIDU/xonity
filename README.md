# 🚀 XONITY - Monitor con ESP32

**Advertencia:** Este código tiene fines educativos y de investigación. Debe usarse de manera responsable. El autor no se hace responsable del uso indebido.

---

## 🎯 ¿Qué es XONITY?

XONITY es un sistema de monitoreo residencial de bajo costo basado en ESP32 y sensor PIR que detecta movimiento y envía alertas por correo electrónico en tiempo real. Consta de dos componentes principales:

- **`start.py`** - Lanzador universal que verifica dependencias y ejecuta el programa principal
- **`xonity.py`** - Servidor Flask que recibe datos del ESP32, gestiona alertas y muestra interfaz web

Está especialmente diseñado para ser económico, de código abierto y fácil de implementar en cualquier hogar.

---

### Características principales:

| Característica | Descripción |
|----------------|-------------|
| ✅ **Detección de movimiento** | Sensor PIR HC-SR501 conectado a ESP32 |
| ✅ **Alertas por correo** | Notificaciones instantáneas vía Gmail |
| ✅ **Monitor de conexión** | Detecta desconexiones del ESP32 automáticamente |
| ✅ **Interfaz web** | Visualización en tiempo real desde cualquier navegador |
| ✅ **Registro en Excel** | Historial completo de todos los eventos |
| ✅ **Acceso remoto** | Vía Cloudflare Tunnel (gratuito) |
| ✅ **Código QR** | Acceso móvil inmediato escaneando el código |
| ✅ **Cooldown inteligente** | Evita spam de correos (5 minutos entre alertas) |
| ✅ **Multiplataforma** | Funciona en Windows, Linux, macOS y Raspberry Pi |
| ✅ **Bajo consumo** | Corre en equipos con 512 MB RAM |

---

## 📥 Instalación

### Opción 1 - Clonar desde GitHub

```bash
git clone https://github.com/XONIDU/xonity.git
cd xonity
```

### Opción 2 - Comando `xoninstall` (recomendado para futuras herramientas XONI)

Agrega la siguiente función a tu `~/.bashrc`:

```bash
echo 'xoninstall() { if [ -z "$1" ]; then echo "Uso: xoninstall <repo>"; echo "Ej: xoninstall xoniran"; else git clone "https://github.com/XONIDU/$1.git"; fi }' >> ~/.bashrc
source ~/.bashrc
```

Luego simplemente escribe:

```bash
xoninstall xonity
cd xonity
pip install -r requisitos.txt
python start.py
```

> **Nota:** Esta función te servirá para instalar cualquier otra herramienta futura de XONIDU (por ejemplo `xoninstall xonichat`).

### Opción 3 - Windows con `INICIAR_XONITY.bat` (recomendado)

En Windows, simplemente haz doble clic en el archivo `INICIAR_XONITY.bat` incluido en el proyecto. Este script:

- Solicita automáticamente permisos de administrador
- Verifica e instala las dependencias necesarias
- Ejecuta el servidor XONITY
- Muestra la URL de acceso local

El archivo `INICIAR_XONITY.bat` contiene:

```batch
@echo off
title XONINAS 2026 - NAS Local con Carpetas Protegidas
color 0A

:: ============================================================
:: IR AL DIRECTORIO DONDE ESTA EL SCRIPT .BAT
:: ============================================================
cd /d "%~dp0"

:: ============================================================
:: SOLICITAR PERMISOS DE ADMINISTRADOR
:: ============================================================
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando permisos de administrador...
    echo.
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /B
)

:: ============================================================
:: VERIFICAR QUE start.py EXISTE
:: ============================================================
if not exist "%~dp0start.py" (
    echo [ERROR] No se encuentra start.py en esta carpeta
    echo.
    echo Ruta actual: %~dp0
    echo.
    echo Asegurate de que start.py esta en la misma carpeta que este .bat
    echo.
    pause
    exit /B
)

:: ============================================================
:: VERIFICAR QUE PYTHON ESTA INSTALADO
:: ============================================================
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo.
    echo Descarga Python desde: https://www.python.org/downloads/
    echo.
    pause
    exit /B
)

:: ============================================================
:: VERIFICAR DEPENDENCIAS (opcional, se puede eliminar)
:: ============================================================
echo [INFO] Verificando dependencias...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Flask no instalado. Instalando...
    pip install flask
)

:: ============================================================
:: EJECUTAR start.py CON PERMISOS DE ADMINISTRADOR
:: ============================================================
cls
echo ============================================================
echo           XONINAS 2026 - NAS Local
echo              (Modo Administrador)
echo ============================================================
echo.
echo [OK] Permisos de administrador obtenidos
echo.
echo [INFO] Directorio de trabajo: %~dp0
echo.
echo Iniciando XONINAS...
echo.
echo [INFO] Sistema de almacenamiento con carpetas protegidas
echo [INFO] Accede a: http://localhost:5000
echo [INFO] Desde tu red local: http://<TU-IP>:5000
echo.
echo Presiona Ctrl+C para detener el servidor
echo ============================================================
echo.

python start.py

pause
```

---

## ✅ Requisitos

- **Python 3.6+** instalado
- **Conexión a Internet** (para alertas por correo)
- **Cuenta Gmail** con token de aplicación
- **Hardware:**
  - ESP32 (modelo 30 pines con microUSB)
  - Sensor PIR HC-SR501
  - Cables jumper
- **Dependencias Python** listadas en `requisitos.txt`

---

## 🔧 Hardware - Conexiones

| Sensor PIR | ESP32 (30 pines) |
|------------|------------------|
| VCC | 3.3V |
| GND | GND |
| OUT | GPIO 4 |

**Alimentación:** El ESP32 se alimenta vía microUSB (cualquier cargador de celular).

---

## 🔑 Configuración de Gmail (Token de aplicación)

1. Activa **verificación en dos pasos** en tu cuenta Google
2. Ve a: https://myaccount.google.com/apppasswords
3. Selecciona:
   - **App:** "Correo"
   - **Dispositivo:** "Otra (nombre personalizado)"
4. Escribe **"XONITY"** y genera
5. **Copia el token de 16 dígitos** (ej: abcd efgh ijkl mnop)

---

## 📦 Instalación de dependencias por plataforma

### 🐧 Arch Linux / Manjaro

```bash
# Instalar dependencias del sistema
sudo pacman -S python-pip

# Instalar dependencias Python
pip install -r requisitos.txt --break-system-packages
```

### 🐧 Ubuntu / Debian / antiX / Raspberry Pi OS

```bash
# Actualizar repositorios
sudo apt update

# Instalar dependencias del sistema
sudo apt install python3 python3-pip -y

# Instalar dependencias Python
pip3 install -r requisitos.txt --break-system-packages
```

### 🍎 macOS

```bash
# Instalar dependencias Python
pip3 install -r requisitos.txt
```

### 🪟 Windows

**Opción A - Con el script .bat (recomendado):**
- Haz doble clic en `INICIAR_XONITY.bat`
- El script instalará las dependencias automáticamente

**Opción B - Manual:**
1. Instala Python 3 desde [python.org](https://www.python.org/downloads/)
2. Abre una terminal (cmd o PowerShell) y ejecuta:

```bash
pip install -r requisitos.txt
```

---

## 🚀 Uso

### 1. Ejecutar el servidor

```bash
python start.py
# o
python3 start.py
```

En Windows, también puedes hacer doble clic en `INICIAR_XONITY.bat`.

El lanzador verificará las dependencias y automáticamente ejecutará `xonity.py`.

### 2. Configurar credenciales (primera vez)

Al iniciar, el programa pedirá:

```
📧 Tu Gmail: tu.correo@gmail.com
🔑 Token de app (16 dígitos): abcd efgh ijkl mnop
📨 Correo destino: destino@gmail.com
```

### 3. Acceder a la interfaz web

- **Local:** `http://localhost:5000` o `http://[IP-DEL-SERVIDOR]:5000`
- **Móvil:** Escanea el código QR que aparece en la terminal

### 4. Programar el ESP32

Abre `esp32.ino` en Arduino IDE y configura:

```cpp
// ===== CONFIGURACIÓN WIFI =====
#define WIFI_SSID "TU_RED_WIFI"
#define WIFI_PASS "TU_CONTRASEÑA"

// ===== CONFIGURACIÓN DEL SERVIDOR =====
// Opción 1: ACCESO REMOTO con Cloudflare Tunnel
#define SERVER_URL "ejemplo.trycloudflare.com"
#define SERVER_PORT 443
#define USE_HTTPS true

// Opción 2: RED LOCAL (para pruebas)
// #define SERVER_URL "192.168.1.84"
// #define SERVER_PORT 5000
// #define USE_HTTPS false

// ===== PIN DEL SENSOR =====
#define IR_SENSOR_PIN 4
```

---

## 🌐 Acceso remoto con Cloudflare Tunnel (opcional)

### Instalación:

```bash
# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Arch Linux
sudo pacman -S cloudflared

# Ejecutar túnel
cloudflared tunnel --url http://localhost:5000
```

### Salida esperada:

```
Your quick Tunnel has been created! Visit it at:
https://ejemplo-aleatorio-123.trycloudflare.com
```

Usa esta URL en la configuración del ESP32.

---

## 📋 Tipos de alertas por correo

| Evento | Asunto | Cooldown |
|--------|--------|----------|
| 🚨 Movimiento | "ALERTA: Movimiento detectado" | 10 seg (ESP32) |
| ⚠️ Desconexión | "ALERTA: ESP32 Desconectado" | 5 minutos |
| 🔄 Reconexión | "ALERTA: ESP32 Reconectado" | 5 minutos |

---

## 📊 Registro automático

Todos los eventos se guardan en `casa1.xlsx` con formato:

| Tipo | Estado | Hora |
|------|--------|------|
| Movimiento | Detectado | 2026-03-16 14:32:15 |
| Conexión | Desconectado | 2026-03-16 16:45:22 |
| Conexión | Reconectado | 2026-03-16 16:45:30 |

---

## 📁 Archivos del proyecto

| Archivo | Descripción |
|---------|-------------|
| `start.py` | Lanzador universal (verifica dependencias y ejecuta) |
| `xonity.py` | Servidor principal con Flask |
| `esp32.ino` | Firmware para programar el ESP32 |
| `templates/index.html` | Interfaz web de monitoreo |
| `requisitos.txt` | Dependencias Python |
| `diagrama.pdf` | Diagrama de conexiones |
| `README.md` | Este archivo de documentación |
| `INICIAR_XONITY.bat` | Script para Windows (doble clic para ejecutar) |
| `casa1.xlsx` | Registro automático de eventos (se genera solo) |

---

## 📱 Código QR

Al iniciar el servidor, se genera automáticamente un código QR con la URL local. ¡Escanéalo con tu móvil para acceder rápidamente a la interfaz web!

---

## 🔒 Consideraciones de seguridad

- No compartas tu token de Gmail públicamente
- Las credenciales se piden al inicio y solo se almacenan en memoria
- El túnel de Cloudflare proporciona cifrado HTTPS automático
- En red local, considera usar siempre HTTPS para comunicaciones sensibles
- Este programa es **SOLO para fines educativos y de investigación**

---

## 🐛 Problemas comunes

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: No module named 'flask'` | Ejecuta: `pip install flask` |
| El ESP32 no se conecta | Verifica WiFi y URL del servidor |
| No llegan correos | Usa token de app (no contraseña normal) |
| Error 401 en correo | El token debe ser de 16 dígitos sin espacios |
| QR no se ve | Terminal debe soportar caracteres UTF-8 |
| Error `--break-system-packages` | Usa `pip install --user` o entorno virtual |

---

## 🧪 Requisitos mínimos del sistema

### Servidor:
- **CPU:** Cualquier procesador (probado en Raspberry Pi Zero)
- **RAM:** 512 MB (87 MB utilizados)
- **Almacenamiento:** 10 MB libres
- **Python:** 3.6 o superior

### Hardware:
- **ESP32:** Modelo 30 pines con microUSB
- **Sensor:** PIR HC-SR501
- **Cables:** 3 jumper hembra-hembra

---

## ✉️ Contacto y Créditos

- **Proyecto:** XONITY
- **Contacto:** xonidu@gmail.com
- **Creador:** Darian Alberto Camacho Salas
- **Coautor:** Oscar Rodolfo Barragán Pérez
- **Institución:** FESC-UNAM
- **GitHub:** [@XONIDU](https://github.com/XONIDU)
- **#Somos XONINDU**

---

**XONITY v1.0** - Marzo 2026  
*"Tecnología accesible para seguridad residencial"*