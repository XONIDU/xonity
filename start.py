from flask import Flask, request, jsonify, render_template
import threading
import time
import smtplib
from datetime import datetime
import pandas as pd
import os

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
EMAIL = input("📧 Tu Gmail: ").strip()
TOKEN = input("🔑 Token de app (16 dígitos): ").strip()
DESTINO = input("📨 Correo destino: ").strip()

def enviar_correo(asunto, mensaje):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, TOKEN)
        server.sendmail(EMAIL, DESTINO, f"Subject: {asunto}\n\n{mensaje}")
        server.quit()
        print(f"📧 Correo enviado: {asunto}")
        return True
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")
        return False

# --- Guardar Excel ---
def registrar(tipo, estado, hora):
    global df
    try:
        nuevo_registro = pd.DataFrame([{"Tipo": tipo, "Estado": estado, "Hora": hora}])
        df = pd.concat([df, nuevo_registro], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)
        print(f"📊 Registro guardado: {tipo} - {estado}")
    except Exception as e:
        print("❌ Error guardando Excel:", e)

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
                # Enviar correo si ha pasado suficiente tiempo
                if tiempo_actual - ultimo_correo_desconectado > COOLDOWN_CORREO:
                    enviar_correo("⚠️ ESP32 Desconectado", f"El ESP32 se desconectó a las {hora}")
                    ultimo_correo_desconectado = tiempo_actual
                registrar("Conexión", "Desconectado", hora)
                print(f"⚠️ Desconexión detectada a las {hora}")
            else:
                if tiempo_actual - ultimo_correo_reconectado > COOLDOWN_CORREO:
                    enviar_correo("🔄 ESP32 Reconectado", f"El ESP32 se reconectó a las {hora}")
                    ultimo_correo_reconectado = tiempo_actual
                registrar("Conexión", "Reconectado", hora)
                print(f"🔄 Reconectado: {hora}")
        
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
    detected = False  # reset movimiento
    print(f"📶 Ping recibido - {datetime.now().strftime('%H:%M:%S')}")
    return jsonify({"status": "ok"})

@app.route('/motion', methods=['POST'])
def motion():
    global last_ping, last_motion, detected
    last_ping = time.time()
    detected = True
    last_motion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Registrar en Excel
    registrar("Movimiento", "Detectado", last_motion)
    
    # Enviar correo
    enviar_correo("🚨 Movimiento detectado", f"Se detectó movimiento en el sensor IR a las {last_motion}")
    
    print(f"🚶 Movimiento detectado a las {last_motion}")
    return jsonify({"status": "motion_received"})

@app.route('/registrar_esp32', methods=['POST'])
def registrar_esp32():
    data = request.json
    if data:
        mac = data.get('mac', 'desconocida')
        ip = data.get('ip', 'desconocida')
        print(f"✅ ESP32 registrado - MAC: {mac}, IP: {ip}")
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
    print("\n" + "="*50)
    print("🚀 XONITY - SERVIDOR DE MONITOREO")
    print("="*50)
    print(f"📧 Correo configurado: {EMAIL}")
    print(f"📨 Enviando a: {DESTINO}")
    print(f"📊 Excel: {EXCEL_FILE}")
    print("="*50)
    
    # Iniciar monitor en segundo plano
    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()
    print("📡 Monitor de conexión iniciado")
    
    # Iniciar servidor
    print("🌐 Servidor web: http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(host="0.0.0.0", port=5000, debug=False)
