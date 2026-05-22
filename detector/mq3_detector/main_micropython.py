"""
main_micropython.py - Detector MQ-3 para MicroPython

Pensado para una placa con MicroPython y un MCP3008 por SPI,
por ejemplo Raspberry Pi Pico / Pico W.
"""

from machine import Pin, SPI
from time import sleep, ticks_ms, ticks_diff

from config_micropython import (
    LED_VERDE,
    LED_ROJO,
    BUZZER,
    SPI_ID,
    SPI_BAUDRATE,
    SPI_SCK,
    SPI_MOSI,
    SPI_MISO,
    SPI_CS,
    ADC_CANAL,
    UMBRAL_ADVERTENCIA,
    UMBRAL_PELIGRO,
    TIEMPO_CALENTAMIENTO,
)


led_verde = Pin(LED_VERDE, Pin.OUT)
led_rojo = Pin(LED_ROJO, Pin.OUT)
buzzer = Pin(BUZZER, Pin.OUT)
cs = Pin(SPI_CS, Pin.OUT, value=1)
spi = SPI(
    SPI_ID,
    baudrate=SPI_BAUDRATE,
    polarity=0,
    phase=0,
    sck=Pin(SPI_SCK),
    mosi=Pin(SPI_MOSI),
    miso=Pin(SPI_MISO),
)


def leer_canal(canal=0):
    if not 0 <= canal <= 7:
        raise ValueError("El canal del MCP3008 debe estar entre 0 y 7.")

    tx = bytearray((1, (8 + canal) << 4, 0))
    rx = bytearray(3)
    cs.value(0)
    spi.write_readinto(tx, rx)
    cs.value(1)
    return ((rx[1] & 0x03) << 8) | rx[2]


def adc_a_voltaje(valor):
    return round((valor / 1023) * 3.3, 2)


def adc_a_ppm(valor):
    return round((valor / 1023) * 500, 1)


def evaluar_nivel(valor):
    if valor >= UMBRAL_PELIGRO:
        return "peligro"
    if valor >= UMBRAL_ADVERTENCIA:
        return "advertencia"
    return "normal"


def actualizar_salidas(nivel):
    led_verde.value(1 if nivel == "normal" else 0)
    led_rojo.value(1 if nivel in ("advertencia", "peligro") else 0)
    buzzer.value(1 if nivel == "peligro" else 0)


def apagar_todo():
    led_verde.value(0)
    led_rojo.value(0)
    buzzer.value(0)
    cs.value(1)


def main():
    print("=== Detector MQ-3 MicroPython ===")
    print("Calentando sensor ({}s)...".format(TIEMPO_CALENTAMIENTO))
    inicio = ticks_ms()

    try:
        while True:
            transcurrido_ms = ticks_diff(ticks_ms(), inicio)
            calentando = transcurrido_ms < (TIEMPO_CALENTAMIENTO * 1000)
            valor = leer_canal(ADC_CANAL)
            voltaje = adc_a_voltaje(valor)
            ppm = adc_a_ppm(valor)

            if calentando:
                porcentaje = min(100, int((transcurrido_ms * 100) / (TIEMPO_CALENTAMIENTO * 1000)))
                print("Calentando... {:3d}%  ADC:{:4d}".format(porcentaje, valor))
            else:
                nivel = evaluar_nivel(valor)
                actualizar_salidas(nivel)
                print("[{}] ADC:{:4d}  {}V  ~{}ppm".format(nivel.upper(), valor, voltaje, ppm))

            sleep(0.5)
    except KeyboardInterrupt:
        print("Detenido.")
    finally:
        apagar_todo()


main()
