# config_micropython.py - pines y umbrales para MicroPython

# GPIO para LEDs y buzzer en la placa MicroPython.
LED_VERDE = 22
LED_ROJO = 27
BUZZER = 17

# SPI para leer el MCP3008.
SPI_ID = 0
SPI_BAUDRATE = 1_000_000
SPI_SCK = 18
SPI_MOSI = 19
SPI_MISO = 16
SPI_CS = 20

# Canal del MCP3008 donde esta conectado el MQ-3.
ADC_CANAL = 0

# Umbrales ADC (0-1023).
UMBRAL_ADVERTENCIA = 400
UMBRAL_PELIGRO = 700

# Tiempo de calentamiento del sensor.
TIEMPO_CALENTAMIENTO = 20
