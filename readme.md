# Raspberry Pi Pico LoRa Transceiver

This project enables LoRa (Long Range) communication between two Raspberry Pi Pico boards using MicroPython and the SX127x LoRa module.

## Features

-   **Sender/Receiver Model:** Includes separate scripts for a sending and a receiving node.
-   **MicroPython:** Built to run on the Raspberry Pi Pico with MicroPython.
-   **Easy to Use:** Simple scripts to demonstrate the core functionality of LoRa communication.

## Hardware Requirements

*   2 x Raspberry Pi Pico
*   2 x SX127x-based LoRa module (e.g., Adafruit RFM95W, HopeRF RFM9x)
*   Jumper wires for connections

## Software Requirements

*   [MicroPython for Raspberry Pi Pico](https://micropython.org/download/RPI_PICO/)
*   The `pyLora` library (the one we fixed)

## Installation

1.  **Flash MicroPython:** If you haven't already, flash MicroPython onto both of your Raspberry Pi Picos.
2.  **Connect Hardware:** Wire the LoRa module to the Raspberry Pi Pico. You will need to connect the following pins:
    - `VCC` to `3V3`
    - `GND` to `GND`
    - `SCK` to `GP10` (SPI1 SCK)
    - `MOSI` to `GP11` (SPI1 TX)
    - `MISO` to `GP8` (SPI1 RX)
    - `NSS` (or `CS`) to `GP9` (SPI1 CSn)
    - `RESET` to `GP12`
    - `DIO0` to `GP13`
    *(Note: You can use other pins, but you will need to update the pin definitions in the scripts accordingly.)*
3.  **Upload Files:**
    - Create a `lib` directory on your Pico.
    - Upload the `pyLora.py` library file into the `/lib` directory.
    - Upload `sender.py` to one Pico and `receiver.py` to the other.

## Usage

-   **Receiver:** Run the `receiver.py` script on one Pico. It will enter receive mode and wait for messages.
-   **Sender:** Run the `sender.py` script on the other Pico. It will send a "Hello World" message every 5 seconds.

When a message is received, the receiver Pico will print the message content, RSSI, and SNR to the console.

## Contributing

Contributions are welcome! If you have suggestions for improvements, please open an issue or submit a pull request.
