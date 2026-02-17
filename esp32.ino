#include <WiFi.h>
#include <WiFiClientSecure.h>

// ===== CONFIGURACIÓN =====
#define WIFI_SSID ""
#define WIFI_PASS ""

// === USAR LINK DEL TUNNEL ===
#define SERVER_HOST "ejemplo.trycloudflare.com"  // Link del tunnel
#define SERVER_PORT 443                           // Puerto HTTPS
#define USE_HTTPS true

// === O USAR IP LOCAL (COMENTADO) ===
// #define SERVER_HOST "192.168.1.84"
// #define SERVER_PORT 5000
// #define USE_HTTPS false

#define IR_SENSOR_PIN 4

// ===== VARIABLES GLOBALES =====
WiFiClient client;
WiFiClientSecure secureClient;  // Para HTTPS
String macAddress;
String nodeIP;
unsigned long lastPing = 0;
unsigned long lastMotion = 0;
bool lastSensorState = false;

const unsigned long PING_INTERVAL = 5000;
const unsigned long MOTION_COOLDOWN = 10000;

// ===== ENVIAR PETICIÓN HTTP/HTTPS =====
bool sendHttpPost(const String& path, const String& data) {
    bool conectado = false;
    
    if (USE_HTTPS) {
        // Configurar cliente HTTPS
        secureClient.setInsecure();  // Acepta cualquier certificado
        conectado = secureClient.connect(SERVER_HOST, SERVER_PORT);
    } else {
        conectado = client.connect(SERVER_HOST, SERVER_PORT);
    }
    
    if (!conectado) {
        Serial.println("❌ No se pudo conectar al servidor");
        Serial.print("   Host: ");
        Serial.print(SERVER_HOST);
        Serial.print(":");
        Serial.println(SERVER_PORT);
        return false;
    }
    
    // Usar el cliente apropiado
    WiFiClient *cli = USE_HTTPS ? (WiFiClient*)&secureClient : (WiFiClient*)&client;
    
    cli->println("POST " + path + " HTTP/1.1");
    cli->println("Host: " + String(SERVER_HOST));
    cli->println("Content-Type: application/x-www-form-urlencoded");
    cli->println("Content-Length: " + String(data.length()));
    cli->println("Connection: close");
    cli->println();
    cli->println(data);
    
    // Esperar respuesta
    unsigned long timeout = millis();
    while (cli->connected() && !cli->available()) {
        if (millis() - timeout > 3000) {
            cli->stop();
            return false;
        }
        delay(10);
    }
    
    // Leer respuesta (opcional)
    String response = "";
    while (cli->available()) {
        response += (char)cli->read();
    }
    
    // Mostrar primeras líneas de respuesta
    if (response.length() > 0) {
        int endLine = response.indexOf('\n');
        if (endLine > 0) {
            Serial.print("📥 Respuesta: ");
            Serial.println(response.substring(0, endLine));
        }
    }
    
    cli->stop();
    return true;
}

// ===== ENVIAR PING =====
void sendPing() {
    if (sendHttpPost("/ping", "ping=1")) {
        Serial.println("📶 Ping enviado a " + String(SERVER_HOST));
    } else {
        Serial.println("❌ Error enviando ping");
    }
}

// ===== ENVIAR MOVIMIENTO =====
void sendMotion() {
    if (sendHttpPost("/motion", "motion=1")) {
        Serial.println("🚶 Movimiento reportado a " + String(SERVER_HOST));
    } else {
        Serial.println("❌ Error reportando movimiento");
    }
}

// ===== RESOLVER IP DEL HOST (DEBUG) =====
void resolveHostIP() {
    IPAddress resolvedIP;
    if (WiFi.hostByName(SERVER_HOST, resolvedIP)) {
        Serial.print("🌐 Host resuelto: ");
        Serial.print(SERVER_HOST);
        Serial.print(" → ");
        Serial.println(resolvedIP);
    } else {
        Serial.println("❌ No se pudo resolver el host");
    }
}

// ===== SETUP =====
void setup() {
    Serial.begin(115200);
    delay(1000);
    
    pinMode(IR_SENSOR_PIN, INPUT);
    
    Serial.println("\n=================================");
    Serial.println("🔧 XONITY - SENSOR IR CON LINK");
    Serial.println("=================================");
    
    Serial.print("📡 Servidor: ");
    Serial.print(SERVER_HOST);
    Serial.print(":");
    Serial.println(SERVER_PORT);
    Serial.print("🔒 HTTPS: ");
    Serial.println(USE_HTTPS ? "Sí" : "No");
    
    // Obtener MAC
    macAddress = WiFi.macAddress();
    Serial.print("📱 MAC: ");
    Serial.println(macAddress);
    
    // Conectar WiFi
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("📡 Conectando WiFi");
    
    unsigned long startAttempt = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - startAttempt < 20000) {
        delay(500);
        Serial.print(".");
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        nodeIP = WiFi.localIP().toString();
        Serial.println("\n✅ WiFi conectado!");
        Serial.print("🌐 IP local ESP32: ");
        Serial.println(nodeIP);
        
        // Resolver IP del host
        resolveHostIP();
        
        // Ping inicial
        delay(1000);
        sendPing();
        lastPing = millis();
        
    } else {
        Serial.println("\n❌ Error WiFi - Reiniciando...");
        delay(3000);
        ESP.restart();
    }
}

// ===== LOOP =====
void loop() {
    if (millis() - lastPing >= PING_INTERVAL) {
        lastPing = millis();
        sendPing();
    }
    
    bool currentState = digitalRead(IR_SENSOR_PIN);
    
    if (currentState == HIGH && lastSensorState == LOW) {
        if (millis() - lastMotion >= MOTION_COOLDOWN) {
            lastMotion = millis();
            sendMotion();
        }
    }
    
    lastSensorState = currentState;
    
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("⚠️ WiFi desconectado, reconectando...");
        WiFi.reconnect();
        delay(2000);
    }
    
    delay(50);
}
