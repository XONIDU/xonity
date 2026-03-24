from flask import Flask, request, jsonify, render_template
import threading
import time
import smtplib
from datetime import datetime
import pandas as pd
import os
import qrcode
from io import StringIO
import logging
import socket

app = Flask(__name__)

# --- Variables globales ---
last_ping = 0
ESP_TIMEOUT = 15
connected = False
detected = False
last_motion = "Nunca"

# --- Excel ---
EXCEL_FILE = "casa1.xlsx"
try:
    df = pd.read_excel(EXCEL_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=["Tipo", "Estado", "Hora"])
    df.to_excel(EXCEL_FILE, index=False)

# --- Credenciales de correo FIJAS ---
EMAIL = "xonidu@gmail.com"
TOKEN = "rohhwgfauvfkyidv"
DESTINO = "xonidu@gmail.com"

print("\n" + "="*50)
print("🔧 XONITY - CORREO CONFIGURADO")
print("="*50)
print(f"📧 Cuenta: {EMAIL}")
print(f"📨 Enviando a: {DESTINO}")
print("="*50)

def obtener_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def generar_qr_con_url(url):
    qr = qrcode.QRCode(version=1, box_size=2, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    qr_ascii = StringIO()
    qr.print_ascii(out=qr_ascii, invert=True)
    return qr_ascii.getvalue()

def enviar_correo(asunto, mensaje):
    """Envía correo y muestra resultado en terminal"""
    try:
        print(f"📧 [CORREO] Intentando enviar: {asunto}")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, TOKEN)
        server.sendmail(EMAIL, DESTINO, f"Subject: {asunto}\n\n{mensaje}")
        server.quit()
        print(f"✅ [CORREO] Enviado correctamente: {asunto}")
        return True
    except Exception as e:
        print(f"❌ [CORREO] Error: {e}")
        return False

def registrar(tipo, estado, hora):
    global df
    try:
        nuevo_registro = pd.DataFrame([{"Tipo": tipo, "Estado": estado, "Hora": hora}])
        df = pd.concat([df, nuevo_registro], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        print(f"📊 [EXCEL] Registrado: {tipo} - {estado} a las {hora}")
    except Exception as e:
        print(f"❌ [EXCEL] Error: {e}")

def monitor():
    """Monitorea la conexión del ESP32 y muestra estado en terminal"""
    global last_ping, connected
    estado_anterior = False
    ultimo_correo_desconectado = 0
    ultimo_correo_reconectado = 0
    COOLDOWN_CORREO = 300
    
    print("📡 [MONITOR] Iniciado. Esperando pings del ESP32...")
    
    while True:
        tiempo_sin_ping = time.time() - last_ping
        conectado = tiempo_sin_ping <= ESP_TIMEOUT
        tiempo_actual = time.time()

        # Mostrar estado cada 10 segundos (solo si hay cambios o para debug)
        if conectado:
            if tiempo_sin_ping > 5:  # Solo mostrar si lleva más de 5s sin ping
                pass  # Silencioso para no llenar terminal
        else:
            if int(tiempo_sin_ping) % 5 == 0:  # Mostrar cada 5s cuando está desconectado
                print(f"⚠️ [MONITOR] Sin ping por {int(tiempo_sin_ping)}s | Desconectado")

        if conectado != estado_anterior:
            estado_anterior = conectado
            hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if not conectado:
                print(f"🔴 [MONITOR] ¡DESCONEXIÓN detectada! Último ping hace {tiempo_sin_ping:.0f}s")
                if tiempo_actual - ultimo_correo_desconectado > COOLDOWN_CORREO:
                    enviar_correo("⚠️ ESP32 Desconectado", f"El ESP32 se desconectó a las {hora}")
                    ultimo_correo_desconectado = tiempo_actual
                registrar("Conexión", "Desconectado", hora)
            else:
                print(f"🟢 [MONITOR] ¡RECONEXIÓN! ESP32 activo nuevamente")
                if tiempo_actual - ultimo_correo_reconectado > COOLDOWN_CORREO:
                    enviar_correo("🔄 ESP32 Reconectado", f"El ESP32 se reconectó a las {hora}")
                    ultimo_correo_reconectado = tiempo_actual
                registrar("Conexión", "Reconectado", hora)
        
        time.sleep(1)

# --- Rutas ---
@app.route('/')
def index():
    return render_template('index.html', 
                         last_ping=last_ping,
                         ESP_TIMEOUT=ESP_TIMEOUT,
                         detected=detected,
                         last_motion=last_motion)

@app.route('/ping', methods=['POST'])
def ping():
    global last_ping, detected
    last_ping = time.time()
    detected = False
    hora = datetime.now().strftime("%H:%M:%S")
    print(f"📶 [PING] Recibido a las {hora}")
    return jsonify({"status": "ok"})

@app.route('/motion', methods=['POST'])
def motion():
    global last_ping, last_motion, detected
    last_ping = time.time()
    detected = True
    last_motion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"🚨 [MOVIMIENTO] ¡DETECTADO! a las {last_motion}")
    
    registrar("Movimiento", "Detectado", last_motion)
    enviar_correo("🚨 Movimiento detectado", f"Se detectó movimiento en el sensor IR a las {last_motion}")
    
    return jsonify({"status": "motion_received"})

@app.route('/registrar_esp32', methods=['POST'])
def registrar_esp32():
    data = request.json
    if data:
        mac = data.get('mac', 'desconocida')
        ip = data.get('ip', 'desconocida')
        print(f"📱 [ESP32] Registrado - MAC: {mac}, IP: {ip}")
        return jsonify({"estado": "ok", "mensaje": "Registro exitoso"})
    return jsonify({"estado": "error", "mensaje": "Datos inválidos"})

@app.route('/estado_cluster', methods=['GET'])
def estado_cluster():
    tiempo_sin_ping = time.time() - last_ping
    conectado = tiempo_sin_ping <= ESP_TIMEOUT
    
    return jsonify({
        "estado": "activo",
        "timestamp": time.time(),
        "ultimo_ping": last_ping,
        "conectado": conectado,
        "tiempo_sin_ping": round(tiempo_sin_ping, 2)
    })

@app.context_processor
def utility_processor():
    def now():
        return datetime.now()
    return dict(now=now)

if __name__ == '__main__':
    os.system('clear' if os.name == 'posix' else 'cls')
    
    IP_LOCAL = obtener_ip_local()
    URL_ACCESO = f"http://{IP_LOCAL}:5000"
    
    print("╔" + "═"*50 + "╗")
    print("║" + " "*18 + "XONITY v1.0" + " "*19 + "║")
    print("╚" + "═"*50 + "╝")
    print()
    
    print("🌐 ACCESO A LA INTERFAZ WEB:")
    print(f"   Local: {URL_ACCESO}")
    print()
    
    print("📱 ESCANEA ESTE CÓDIGO QR PARA ACCEDER DESDE TU MÓVIL:")
    print()
    print(generar_qr_con_url(URL_ACCESO))
    print()
    print("🔒 Sistema de monitoreo IoT - Seguridad Residencial")
    print("="*50)
    print()
    print("📡 MONITOR EN TERMINAL ACTIVO:")
    print("   - Esperando pings del ESP32...")
    print("   - Los eventos se mostrarán aquí en tiempo real")
    print("="*50)
    print()
    
    # NO silenciar Flask para ver logs importantes
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)  # Solo mostrar warnings y errores
    
    # Iniciar monitor en segundo plano
    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()
    
    # Iniciar servidor (con logs mínimos)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
