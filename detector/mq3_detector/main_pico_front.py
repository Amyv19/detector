from machine import Pin, ADC
import time

mq3 = ADC(26)

led_verde = Pin(16, Pin.OUT)
led_rojo = Pin(17, Pin.OUT)
buzzer = Pin(15, Pin.OUT)

print("Calentando sensor...")
time.sleep(30)

print("Calibrando...")
suma = 0
for _ in range(40):
    valor = mq3.read_u16()
    suma += valor
    time.sleep(0.2)

BASE = suma // 40
DELTA_GAS = 1500

print("Valor base =", BASE)

while True:
    valor = mq3.read_u16()
    delta_sube = valor - BASE
    voltaje = (valor / 65535) * 3.3

    if delta_sube >= DELTA_GAS:
        led_verde.value(0)
        led_rojo.value(1)
        buzzer.value(1)
        estado = "ALCOHOL DETECTADO"
    else:
        led_verde.value(1)
        led_rojo.value(0)
        buzzer.value(0)
        estado = "NORMAL"

    print(
        "ADC:", valor,
        "| Base:", BASE,
        "| Delta:", delta_sube,
        "| Voltaje:", round(voltaje, 2),
        "|", estado
    )
    time.sleep(0.2)
