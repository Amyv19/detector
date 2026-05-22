#!/usr/bin/env python3
"""
Puente serial -> WebSocket para usar dashboard.html con una placa MicroPython.

Uso:
  python serial_frontend.py COM6
  python serial_frontend.py /dev/ttyACM0

Requiere:
  pip install pyserial websockets
"""

import asyncio
import json
import re
import sys
import time

try:
    import serial
except ImportError:
    raise SystemExit("Falta pyserial. Instala con: pip install pyserial")

try:
    import websockets
except ImportError:
    raise SystemExit("Falta websockets. Instala con: pip install websockets")


LINE_RE = re.compile(
    r"ADC:\s*(?P<adc>\d+)"
    r".*?Base:\s*(?P<base>-?\d+)"
    r".*?(?:Delta|Sube):\s*(?P<delta>-?\d+)"
    r".*?Voltaje:\s*(?P<voltaje>[\d.]+)"
    r".*?\|\s*(?P<estado>ALCOHOL DETECTADO|NORMAL)"
)

clientes = set()
historial = []
t0 = time.time()


def normalizar_estado(estado):
    return "peligro" if estado == "ALCOHOL DETECTADO" else "normal"


def ppm_desde_delta(delta):
    if delta <= 0:
        return 0.0
    return round(min(500.0, delta / 20.0), 1)


def construir_lectura(match):
    adc = int(match.group("adc"))
    base = int(match.group("base"))
    delta = int(match.group("delta"))
    voltaje = float(match.group("voltaje"))
    estado = match.group("estado")
    nivel = normalizar_estado(estado)

    return {
        "ts": round(time.time() - t0, 1),
        "adc": adc,
        "base": base,
        "delta": delta,
        "voltaje": round(voltaje, 2),
        "ppm": ppm_desde_delta(delta),
        "nivel": nivel,
        "calentando": False,
        "warmup_pct": 100,
    }


async def emitir_lectura(lectura):
    historial.append(lectura)
    if len(historial) > 60:
        del historial[:-60]

    if clientes:
        msg = json.dumps({
            "tipo": "lectura",
            "data": lectura,
            "historial": historial[-30:],
        })
        await asyncio.gather(*[c.send(msg) for c in list(clientes)], return_exceptions=True)


async def leer_serial(puerto):
    try:
        ser = serial.Serial(puerto, 115200, timeout=1)
    except Exception as exc:
        raise SystemExit(f"No pude abrir {puerto}: {exc}")

    print(f"Leyendo serial en {puerto}")
    while True:
        line = await asyncio.to_thread(ser.readline)
        if not line:
            continue

        texto = line.decode("utf-8", errors="ignore").strip()
        if not texto:
            continue

        print(texto)
        match = LINE_RE.search(texto)
        if match:
            lectura = construir_lectura(match)
            await emitir_lectura(lectura)


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
    if len(sys.argv) < 2:
        raise SystemExit("Uso: python serial_frontend.py <PUERTO>")

    puerto = sys.argv[1]
    asyncio.create_task(leer_serial(puerto))
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("WebSocket listo en ws://localhost:8765")
        print("Abre dashboard.html en tu navegador")
        await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPuente detenido.")
