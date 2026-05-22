#!/bin/bash
# instalar.sh - ejecuta UNA sola vez en la Raspberry Pi

set -e

MODEL="$(tr -d '\0' </proc/device-tree/model 2>/dev/null || true)"

if ! printf '%s' "$MODEL" | grep -qi "Raspberry Pi"; then
    echo ""
    echo "Este script debe ejecutarse en una Raspberry Pi."
    echo "No lo ejecutes en tu PC con Windows, WSL o Linux de escritorio."
    echo ""
    echo "Flujo correcto:"
    echo "  1. Copia la carpeta a la Raspberry Pi con scp"
    echo "  2. Entra por ssh"
    echo "  3. Ya dentro de la Raspberry Pi, corre: bash instalar.sh"
    echo ""
    exit 1
fi

echo ""
echo "=== Instalador MQ-3 Detector ==="
echo ""

# 1. Actualizar
sudo apt update -y

# 2. Dependencias del sistema
sudo apt install python3-pip python3-dev -y

# 3. Librerias Python
pip3 install spidev RPi.GPIO websockets

echo ""
echo "Instalacion completa."
echo ""
echo "SIGUIENTE PASO - habilitar SPI si no lo has hecho:"
echo "  sudo raspi-config"
echo "  -> Interface Options -> SPI -> Yes -> Finish -> reboot"
echo ""
echo "Para correr en MODO TERMINAL:"
echo "  python3 main.py"
echo ""
echo "Para correr con DASHBOARD WEB:"
echo "  python3 server.py"
echo "  (luego abre dashboard.html en tu navegador)"
echo ""
