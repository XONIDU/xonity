#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XONITY 2026 - Lanzador Universal para Sistema de Monitoreo con ESP32
Este script verifica dependencias y ejecuta xonity.py
Desarrollado por: Darian Alberto Camacho Salas
#Somos XONINDU
"""

import subprocess
import sys
import os
import platform
import shutil
import importlib.util
import time

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    
    @staticmethod
    def supports_color():
        """Verifica si la terminal soporta colores"""
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                return kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                return False
        return True

# Desactivar colores si no hay soporte
if not Colors.supports_color():
    for attr in dir(Colors):
        if not attr.startswith('_') and attr != 'supports_color':
            setattr(Colors, attr, '')

def get_system():
    """Detecta el sistema operativo"""
    return platform.system().lower()

def get_linux_distro():
    """Detecta la distribucion de Linux"""
    if get_system() != 'linux':
        return None
    
    try:
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                content = f.read().lower()
                if 'ubuntu' in content:
                    return 'ubuntu'
                elif 'debian' in content:
                    return 'debian'
                elif 'fedora' in content:
                    return 'fedora'
                elif 'centos' in content:
                    return 'centos'
                elif 'arch' in content:
                    return 'arch'
                elif 'manjaro' in content:
                    return 'manjaro'
                elif 'mint' in content:
                    return 'mint'
        return 'linux-generico'
    except:
        return 'linux-generico'

def get_python_command():
    """Obtiene el comando Python correcto"""
    if get_system() == 'windows':
        return ['python']
    else:
        try:
            subprocess.run(['python3', '--version'], capture_output=True, check=True)
            return ['python3']
        except:
            return ['python']

def print_banner():
    """Muestra el banner de XONITY"""
    sistema = get_system()
    distro = get_linux_distro()
    
    sistema_texto = {
        'windows': 'WINDOWS',
        'linux': f'LINUX ({distro.upper()})' if distro else 'LINUX',
        'darwin': 'MACOS'
    }.get(sistema, 'DESCONOCIDO')
    
    banner = f"""
{Colors.BLUE}{Colors.BOLD}═══════════════════════════════════════════════════════════
                    XONITY 2026 v1.0                    
              Sistema de Monitoreo con ESP32            
              Detección de movimiento + Alertas          
              Seguridad Residencial de Bajo Costo        
                                                          
              Sistema detectado: {sistema_texto}            
                                                          
              Desarrollado por: Darian Alberto            
              Camacho Salas                               
              #Somos XONINDU
═══════════════════════════════════════════════════════════{Colors.END}
    """
    print(banner)

def check_python():
    """Verifica Python instalado"""
    try:
        cmd = get_python_command() + ['--version']
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except:
        return False

def check_python_module(module_name):
    """Verifica si un modulo de Python esta instalado"""
    return importlib.util.find_spec(module_name) is not None

def check_dependencies():
    """Verifica las dependencias de Python necesarias"""
    print(f"\n{Colors.BOLD}Verificando dependencias de Python...{Colors.END}")
    
    dependencias = [
        ('flask', 'flask', 'Servidor web', 'flask'),
        ('pandas', 'pandas', 'Manejo de Excel', 'pandas'),
        ('openpyxl', 'openpyxl', 'Lectura/escritura Excel', 'openpyxl'),
        ('qrcode', 'qrcode', 'Generación de QR', 'qrcode'),
    ]
    
    faltantes = []
    
    for modulo, paquete, desc, import_name in dependencias:
        if check_python_module(import_name):
            print(f"{Colors.GREEN}  ✓ {modulo}: Instalado{Colors.END}")
        else:
            print(f"{Colors.YELLOW}  ✗ {modulo}: No instalado{Colors.END}")
            faltantes.append(paquete)
    
    return faltantes

def install_dependencies(faltantes):
    """Instala las dependencias faltantes"""
    if not faltantes:
        return True
    
    print(f"\n{Colors.BOLD}Instalando dependencias faltantes...{Colors.END}")
    print(f"Paquetes: {', '.join(faltantes)}")
    
    sistema = get_system()
    distro = get_linux_distro()
    
    # Construir comando de instalacion
    cmd = [sys.executable, '-m', 'pip', 'install']
    
    # Agregar opciones segun sistema
    if sistema == 'linux':
        if distro in ['arch', 'manjaro', 'fedora']:
            cmd.append('--break-system-packages')
            print(f"{Colors.YELLOW}Usando --break-system-packages para {distro}{Colors.END}")
        else:
            cmd.append('--user')
    elif sistema == 'darwin':
        cmd.append('--user')
    
    cmd.extend(faltantes)
    
    # Intentar instalacion
    try:
        print(f"Ejecutando: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print(f"{Colors.GREEN}✓ Dependencias instaladas correctamente{Colors.END}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}Error instalando dependencias: {e}{Colors.END}")
        print(f"\n{Colors.YELLOW}Intentando metodo alternativo...{Colors.END}")
        
        # Segundo intento: solo --user
        try:
            cmd2 = [sys.executable, '-m', 'pip', 'install', '--user'] + faltantes
            subprocess.run(cmd2, check=True)
            print(f"{Colors.GREEN}✓ Instaladas con --user{Colors.END}")
            return True
        except:
            print(f"{Colors.RED}✗ Fallo la instalacion{Colors.END}")
            print(f"\nInstala manualmente:")
            print(f"  pip install {' '.join(faltantes)}")
            return False

def verificar_servidor():
    """Verifica si existe el archivo xonity.py"""
    if not os.path.exists('xonity.py'):
        print(f"\n{Colors.RED}Error: No se encuentra xonity.py{Colors.END}")
        print("Asegurate de que xonity.py esta en el mismo directorio")
        return False
    return True

def verificar_importaciones():
    """Verifica que todas las importaciones necesarias funcionen"""
    print(f"\n{Colors.BOLD}Verificando importaciones...{Colors.END}")
    
    modulos = [
        ('flask', 'Flask'),
        ('pandas', 'Pandas'),
        ('openpyxl', 'OpenPyXL'),
        ('qrcode', 'QR Code'),
    ]
    
    todos_ok = True
    for modulo, nombre in modulos:
        try:
            __import__(modulo)
            print(f"{Colors.GREEN}  ✓ {nombre}: OK{Colors.END}")
        except ImportError:
            print(f"{Colors.RED}  ✗ {nombre}: FALLO{Colors.END}")
            todos_ok = False
    
    return todos_ok

def main():
    """Funcion principal"""
    # Limpiar pantalla
    if get_system() == 'windows':
        os.system('cls')
    else:
        os.system('clear')
    
    # Mostrar banner
    print_banner()
    
    # Verificar Python
    if not check_python():
        print(f"\n{Colors.RED}Error: Python no esta instalado{Colors.END}")
        print("Instala Python desde: https://www.python.org/downloads/")
        input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.END}")
        return
    
    python_version = subprocess.run(get_python_command() + ['--version'], 
                                   capture_output=True, text=True).stdout.strip()
    print(f"{Colors.BOLD}Python:{Colors.END} {python_version}")
    print(f"{Colors.BOLD}Directorio:{Colors.END} {os.path.dirname(os.path.abspath(__file__))}")
    
    # Verificar dependencias
    faltantes = check_dependencies()
    
    if faltantes:
        print(f"\n{Colors.YELLOW}Se requieren dependencias adicionales{Colors.END}")
        respuesta = input("¿Instalar automaticamente? (s/n): ")
        
        if respuesta.lower() == 's':
            if not install_dependencies(faltantes):
                print(f"\n{Colors.RED}No se pudieron instalar las dependencias{Colors.END}")
                input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.END}")
                return
        else:
            print(f"\nPuedes instalarlas manualmente con:")
            print("  pip install flask pandas openpyxl qrcode")
            input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.END}")
            return
    
    # Verificar que existe xonity.py
    if not verificar_servidor():
        input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.END}")
        return
    
    # Verificar que las importaciones funcionan
    print(f"\n{Colors.BOLD}Verificando que todo funcione...{Colors.END}")
    if not verificar_importaciones():
        print(f"\n{Colors.RED}Error: No se pueden importar las dependencias necesarias{Colors.END}")
        print("El programa no puede continuar sin estas dependencias")
        input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.END}")
        return
    
    print(f"\n{Colors.BOLD}Iniciando XONITY...{Colors.END}")
    print(f"{Colors.BOLD}Para salir en cualquier momento:{Colors.END} Ctrl+C")
    print("-" * 60)
    
    # EJECUTAR xonity.py
    try:
        python_cmd = get_python_command()
        cmd = python_cmd + ['xonity.py']
        print(f"Ejecutando: {' '.join(cmd)}")
        print("-" * 60)
        time.sleep(1)
        
        # Ejecutar xonity.py
        resultado = subprocess.run(cmd)
        
        if resultado.returncode != 0:
            print(f"\n{Colors.RED}Error: xonity.py termino con codigo {resultado.returncode}{Colors.END}")
            
    except FileNotFoundError:
        print(f"\n{Colors.RED}Error: No se encuentra xonity.py{Colors.END}")
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Servidor detenido por el usuario{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error ejecutando xonity.py: {e}{Colors.END}")
    
    print(f"\n{Colors.BLUE}Gracias por usar XONITY 2026{Colors.END}")
    print(f"{Colors.BLUE}Desarrollado por Darian Alberto Camacho Salas{Colors.END}")
    print(f"{Colors.BLUE}#Somos XONINDU{Colors.END}")
    
    # Pausa al final
    if get_system() != 'windows':
        input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.END}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Saliendo...{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error inesperado: {e}{Colors.END}")
        input(f"\n{Colors.YELLOW}Presiona Enter para salir...{Colors.END}")
