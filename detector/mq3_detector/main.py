#!/usr/bin/env python3
"""
main.py — Detector MQ-3 (modo terminal, sin frontend)
Uso: python3 main.py
"""

import spidev
import RPi.GPIO as GPIO
import time
from config import (
    LED_VERDE, LED_ROJO, BUZZER,
    UMBRAL_ADVERTENCIA, UMBRAL_PELIGRO,
    SPI_BUS, SPI_DEVICE, SPI_MAX_SPEED
)

# ── GPIO ──────────────────────────────────────────
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for pin in (LED_VERDE, LED_ROJO, BUZZER):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# ── SPI / MCP3008 ─────────────────────────────────
spi = spidev.SpiDev()
spi.open(SPI_BUS, SPI_DEVICE)
spi.max_speed_hz = SPI_MAX_SPEED

TIEMPO_CALENTAMIENTO = 20  # segundos

def leer_canal(canal=0):
    r = spi.xfer2([1, (8 + canal) << 4, 0])
    return ((r[1] & 3) << 8) | r[2]

def adc_a_voltaje(v):
    return round((v / 1023.0) * 3.3, 2)

def evaluar_nivel(v):
    if v >= UMBRAL_PELIGRO:     return "peligro"
    if v >= UMBRAL_ADVERTENCIA: return "advertencia"
    return "normal"

def actualizar_gpio(nivel):
    GPIO.output(LED_VERDE, nivel == "normal")
    GPIO.output(LED_ROJO,  nivel in ("advertencia", "peligro"))
    GPIO.output(BUZZER,    nivel == "peligro")

def apagar_todo():
    for pin in (LED_VERDE, LED_ROJO, BUZZER):
        GPIO.output(pin, GPIO.LOW)
    spi.close()
    GPIO.cleanup()

if __name__ == "__main__":
    print("=== Detector MQ-3 ===")
    print(f"Calentando sensor ({TIEMPO_CALENTAMIENTO}s)...\n")
    t0 = time.time()

    try:
        while True:
            elapsed = time.time() - t0
            calentando = elapsed < TIEMPO_CALENTAMIENTO

            valor   = leer_canal(0)
            voltaje = adc_a_voltaje(valor)
            ppm     = round((valor / 1023.0) * 500, 1)

            if calentando:
                pct = min(100, int((elapsed / TIEMPO_CALENTAMIENTO) * 100))
                print(f"\r  Calentando... {pct:3d}%  ADC: {valor:4d}", end="", flush=True)
            else:
                nivel = evaluar_nivel(valor)
                actualizar_gpio(nivel)
                iconos = {"normal": "OK ", "advertencia": "ADV", "peligro": "PEL"}
                print(f"[{iconos[nivel]}]  ADC:{valor:4d}  {voltaje}V  ~{ppm}ppm  → {nivel}")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\nDetenido. Liberando GPIO...")
    finally:
        apagar_todo()
        print("Listo.")
