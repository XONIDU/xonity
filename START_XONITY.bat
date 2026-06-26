@echo off
title XONITY 2026 - Sistema de Monitoreo con ESP32
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
echo           XONITY 2026 - Sistema de Monitoreo con ESP32
echo              (Modo Administrador)
echo ============================================================
echo.
echo [OK] Permisos de administrador obtenidos
echo.
echo Iniciando XONITY...
echo.
echo [INFO] Sistema de monitoreo residencial con ESP32
echo [INFO] Deteccion de movimiento y alertas por correo
echo [INFO] Accede a: http://localhost:5000
echo.
echo Presiona Ctrl+C para detener el servidor
echo ============================================================
echo.

python start.py

pause
