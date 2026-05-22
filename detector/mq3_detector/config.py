# config.py — pines y umbrales del proyecto MQ-3

# ── Pines GPIO (numeración BCM) ──────────────────
LED_VERDE = 22
LED_ROJO  = 27
BUZZER    = 17

# ── SPI ──────────────────────────────────────────
SPI_BUS       = 0
SPI_DEVICE    = 0        # CE0
SPI_MAX_SPEED = 1_350_000

# ── Umbrales ADC (0–1023) ─────────────────────────
# Ajusta después de calibrar en ambiente limpio.
UMBRAL_ADVERTENCIA = 400   # >= LED rojo
UMBRAL_PELIGRO     = 700   # >= LED rojo + buzzer
