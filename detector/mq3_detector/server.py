#!/usr/bin/env python3
"""
server.py — WebSocket server para el dashboard web
Uso: python3 server.py
Luego abre dashboard.html en tu navegador y conecta a ws://<IP-RPi>:8765
"""

import asyncio
import json
import time

try:
    import websockets
except ImportError:
    raise SystemExit("Instala websockets:  pip3 install websockets")

# ── Hardware o simulación ─────────────────────────
try:
    import spidev
    import RPi.GPIO as GPIO
    from config import (
        LED_VERDE, LED_ROJO, BUZZER,
        UMBRAL_ADVERTENCIA, UMBRAL_PELIGRO,
        SPI_BUS, SPI_DEVICE, SPI_MAX_SPEED
    )
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in (LED_VERDE, LED_ROJO, BUZZER):
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEVICE)
    spi.max_speed_hz = SPI_MAX_SPEED
    SIMULACION = False
    print("Modo HARDWARE activo")
except Exception as e:
    SIMULACION = True
    UMBRAL_ADVERTENCIA = 400
    UMBRAL_PELIGRO     = 700
    print(f"Modo SIMULACION activo ({e})")

TIEMPO_CALENTAMIENTO = 20
historial = []
clientes  = set()
t_inicio  = time.time()

def leer_canal(canal=0):
    if SIMULACION:
        import random, math
        t = time.time() - t_inicio
        base = 200 + 160 * abs(math.sin(t / 15))
        return int(base + random.randint(-25, 25))
    r = spi.xfer2([1, (8 + canal) << 4, 0])
    return ((r[1] & 3) << 8) | r[2]

def evaluar_nivel(v):
    if v >= UMBRAL_PELIGRO:     return "peligro"
    if v >= UMBRAL_ADVERTENCIA: return "advertencia"
    return "normal"

def actualizar_gpio(nivel):
    if SIMULACION: return
    GPIO.output(LED_VERDE, nivel == "normal")
    GPIO.output(LED_ROJO,  nivel in ("advertencia", "peligro"))
    GPIO.output(BUZZER,    nivel == "peligro")

async def bucle_sensor():
    global historial
    while True:
        elapsed   = time.time() - t_inicio
        calentando = elapsed < TIEMPO_CALENTAMIENTO
        valor     = leer_canal(0)
        voltaje   = round((valor / 1023.0) * 3.3, 2)
        ppm       = round((valor / 1023.0) * 500, 1)
        nivel     = "calentando" if calentando else evaluar_nivel(valor)

        if not calentando:
            actualizar_gpio(nivel)

        lectura = {
            "ts":          round(elapsed, 1),
            "adc":         valor,
            "voltaje":     voltaje,
            "ppm":         ppm,
            "nivel":       nivel,
            "calentando":  calentando,
            "warmup_pct":  min(100, round((elapsed / TIEMPO_CALENTAMIENTO) * 100))
        }
        historial.append(lectura)
        if len(historial) > 60:
            historial = historial[-60:]

        if clientes:
            msg = json.dumps({"tipo": "lectura", "data": lectura, "historial": historial[-30:]})
            await asyncio.gather(*[c.send(msg) for c in clientes], return_exceptions=True)

        await asyncio.sleep(0.5)

async def handler(ws):
    clientes.add(ws)
    try:
        if historial:
            await ws.send(json.dumps({"tipo": "historial", "historial": historial[-30:]}))
        async for _ in ws:
            pass
    finally:
        clientes.discard(ws)

async def main():
    asyncio.create_task(bucle_sensor())
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket escuchando en ws://0.0.0.0:8765")
        print("Abre dashboard.html y conecta a ws://<IP-DE-TU-RPI>:8765\n")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServidor detenido.")
        if not SIMULACION:
            GPIO.cleanup()
