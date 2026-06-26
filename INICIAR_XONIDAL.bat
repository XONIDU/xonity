@echo off
title XONIDAL 2026 - Universal Serial Bridge
color 0A

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
:: EJECUTAR start.py CON PERMISOS DE ADMINISTRADOR
:: ============================================================
cls
echo ============================================================
echo           XONIDAL 2026 - Universal Serial Bridge
echo              (Modo Administrador)
echo ============================================================
echo.
echo [OK] Permisos de administrador obtenidos
echo.
echo Iniciando XONIDAL...
echo.
echo [INFO] Puente serial universal para control de Arduino
echo [INFO] Interfaz web disponible en: http://localhost:5050
echo [INFO] Usuario: admin  |  Contraseña: 1234
echo.
echo [INFO] Conecta ESP32 y Arduino segun el diagrama
echo [INFO] Configura la IP del ESP32 en la interfaz web
echo.
echo Presiona Ctrl+C para detener el servidor
echo ============================================================
echo.

python start.py

pause
