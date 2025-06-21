from machine import Pin, SPI
import time
from sx127x import SX127x

# --- Pin Definitions ---
# Make sure these match your physical wiring
PIN_ID = {
    'miso': 4,
    'mosi': 3,
    'sck': 2,
    'cs': 5,
    'reset': 6,
    'dio0': 7,
}

# The Pico's built-in LED is usually on pin 25.
# You can also use the alias "LED".
led = machine.Pin("LED", machine.Pin.OUT)

# --- LoRa Parameters ---
LORA_FREQUENCY = 433.0  # MHz - MUST match the receiver's frequency
LORA_TX_POWER = 17      # dBm - Standard power level

# --- Initialize SPI Bus ---
spi = SPI(
    0,
    baudrate=10000000,  # 10MHz
    polarity=0,
    phase=0,
    bits=8,
    firstbit=SPI.MSB,
    sck=Pin(PIN_ID['sck']),
    mosi=Pin(PIN_ID['mosi']),
    miso=Pin(PIN_ID['miso']),
)

# --- Initialize LoRa Module ---
try:
    # Pass parameters to the constructor
    lora = SX127x(
        spi,
        pins=PIN_ID,
        parameters={'frequency': LORA_FREQUENCY, 'tx_power_level': LORA_TX_POWER}
    )
    print("✅ LoRa Sender initialized successfully with full library.")

except Exception as e:
    print(f"❌ Error initializing LoRa module: {e}")
    # Halt execution if the module fails to start
    while True:
        pass

# --- Main Loop ---
packet_counter = 0
while True:
    try:
        # Prepare the message
        message = f"Hello from sender! Packet #{packet_counter}"
        payload = message.encode() # Convert string to bytes

        # The send() method now exists in our new library
        lora.send(payload)
        
        led.on()   # Turn LED ON
        time.sleep(0.2)
        led.off()  # Turn LED OFF
        print(f"✔️ Sent: '{message}'")
        packet_counter += 1
        time.sleep(5) # Wait 5 seconds before sending the next packet

    except Exception as e:
        print(f"❌ An error occurred during sending: {e}")
        time.sleep(5)