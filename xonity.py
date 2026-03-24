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
ESP_TIMEOUT = 15  # segundos para desconexión
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

# --- Pedir credenciales de correo al iniciar ---
print("\n" + "="*50)
print("🔧 XONITY - CONFIGURACIÓN DE CORREO")
print("="*50)
EMAIL = input("Tu Gmail: ").strip()
TOKEN = input("Token de app (16 dígitos): ").strip()
DESTINO = input("Correo destino: ").strip()

def obtener_ip_local():
    """Obtiene la IP local de la máquina"""
    try:
        # Crear un socket temporal para obtener la IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def generar_qr_con_url(url):
    """Genera un código QR con la URL de acceso"""
    qr = qrcode.QRCode(
        version=1,
        box_size=2,
        border=1
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Crear imagen QR en ASCII para terminal
    qr_ascii = StringIO()
    qr.print_ascii(out=qr_ascii, invert=True)
    return qr_ascii.getvalue()

def enviar_correo(asunto, mensaje):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, TOKEN)
        server.sendmail(EMAIL, DESTINO, f"Subject: {asunto}\n\n{mensaje}")
        server.quit()
        return True
    except Exception as e:
        return False

# --- Guardar Excel ---
def registrar(tipo, estado, hora):
    global df
    try:
        nuevo_registro = pd.DataFrame([{"Tipo": tipo, "Estado": estado, "Hora": hora}])
        df = pd.concat([df, nuevo_registro], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
    except Exception as e:
        pass

# --- Monitor conexión ---
def monitor():
    global last_ping, connected
    estado_anterior = False
    ultimo_correo_desconectado = 0
    ultimo_correo_reconectado = 0
    COOLDOWN_CORREO = 300  # 5 minutos entre correos del mismo tipo
    
    while True:
        tiempo_sin_ping = time.time() - last_ping
        conectado = tiempo_sin_ping <= ESP_TIMEOUT
        tiempo_actual = time.time()

        if conectado != estado_anterior:
            estado_anterior = conectado
            hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if not conectado:
                if tiempo_actual - ultimo_correo_desconectado > COOLDOWN_CORREO:
                    enviar_correo("⚠️ ESP32 Desconectado", f"El ESP32 se desconectó a las {hora}")
                    ultimo_correo_desconectado = tiempo_actual
                registrar("Conexión", "Desconectado", hora)
            else:
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
    return jsonify({"status": "ok"})

@app.route('/motion', methods=['POST'])
def motion():
    global last_ping, last_motion, detected
    last_ping = time.time()
    detected = True
    last_motion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    registrar("Movimiento", "Detectado", last_motion)
    enviar_correo("🚨 Movimiento detectado", f"Se detectó movimiento en el sensor IR a las {last_motion}")
    
    return jsonify({"status": "motion_received"})

@app.route('/registrar_esp32', methods=['POST'])
def registrar_esp32():
    data = request.json
    if data:
        mac = data.get('mac', 'desconocida')
        ip = data.get('ip', 'desconocida')
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
    # Limpiar pantalla
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # Obtener IP local
    IP_LOCAL = obtener_ip_local()
    URL_ACCESO = f"http://{IP_LOCAL}:5000"
    
    print("╔" + "═"*50 + "╗")
    print("║" + " "*18 + "XONITY v1.0" + " "*19 + "║")
    print("╚" + "═"*50 + "╝")
    print()
    
    # Mostrar URL de acceso
    print("🌐 ACCESO A LA INTERFAZ WEB:")
    print(f"   Local: {URL_ACCESO}")
    print()
    
    # Generar y mostrar QR code con la URL
    print("📱 ESCANEA ESTE CÓDIGO QR PARA ACCEDER DESDE TU MÓVIL:")
    print()
    print(generar_qr_con_url(URL_ACCESO))
    print()
    print("🔒 Sistema de monitoreo IoT - Seguridad Residencial")
    print("="*50)
    print()
    
    # Silenciar Flask COMPLETAMENTE
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    # Redirigir stdout para silenciar aún más
    import sys
    from contextlib import contextmanager
    
    @contextmanager
    def suppress_output():
        with open(os.devnull, 'w') as devnull:
            old_stdout = sys.stdout
            sys.stdout = devnull
            try:
                yield
            finally:
                sys.stdout = old_stdout
    
    # Iniciar monitor en segundo plano
    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()
    
    # Iniciar servidor CON TODO SILENCIADO
    with suppress_output():
        app.run(host="0.0.0.0", port=5000, debug=False)
