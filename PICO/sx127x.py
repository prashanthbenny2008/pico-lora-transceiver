from machine import Pin, SPI
import time

class SX127x:
    """
    SX127x LoRa radio driver for MicroPython.
    """
    # --- Register Map ---
    REG_FIFO = 0x00
    REG_OP_MODE = 0x01
    REG_FRF_MSB = 0x06
    REG_FRF_MID = 0x07
    REG_FRF_LSB = 0x08
    REG_PA_CONFIG = 0x09
    REG_LNA = 0x0C
    REG_FIFO_ADDR_PTR = 0x0D
    REG_FIFO_TX_BASE_ADDR = 0x0E
    REG_FIFO_RX_BASE_ADDR = 0x0F
    REG_FIFO_RX_CURRENT_ADDR = 0x10
    REG_IRQ_FLAGS = 0x12
    REG_RX_NB_BYTES = 0x13
    REG_PKT_SNR_VALUE = 0x19
    REG_PKT_RSSI_VALUE = 0x1A
    REG_MODEM_CONFIG_1 = 0x1D
    REG_MODEM_CONFIG_2 = 0x1E
    REG_PREAMBLE_MSB = 0x20
    REG_PREAMBLE_LSB = 0x21
    REG_PAYLOAD_LENGTH = 0x22
    REG_MODEM_CONFIG_3 = 0x26
    REG_DIO_MAPPING_1 = 0x40
    REG_VERSION = 0x42
    REG_PA_DAC = 0x4D

    # --- Modes ---
    MODE_SLEEP = 0x00
    MODE_STDBY = 0x01
    MODE_TX = 0x03
    MODE_RX_CONTINUOUS = 0x05
    MODE_RX_SINGLE = 0x06
    MODE_LONG_RANGE_MODE = 0x80

    # --- IRQ Flags ---
    IRQ_TX_DONE_MASK = 0x08
    IRQ_PAYLOAD_CRC_ERROR_MASK = 0x20
    IRQ_RX_DONE_MASK = 0x40

    # --- Constants ---
    FREQ_STEP = 61.03515625

    def __init__(self, spi, pins, parameters):
        """
        Initialize the SX127x object.
        """
        self.cs = Pin(pins['cs'], Pin.OUT)
        self.reset = Pin(pins['reset'], Pin.OUT)
        self.dio0 = Pin(pins['dio0'], Pin.IN)

        self.spi = spi
        self.pins = pins
        self.parameters = parameters

        # Reset the module
        self.reset.value(0)
        time.sleep_ms(50)
        self.reset.value(1)
        time.sleep_ms(50)

        # Check version
        version = self._read_reg(self.REG_VERSION)
        if version != 0x12:
            raise Exception(f"Failed to detect SX127x chip, version: {hex(version)}")

        self.sleep()
        self.init()

    def _write_reg(self, register, value):
        self.cs.value(0)
        self.spi.write(bytes([register | 0x80, value]))
        self.cs.value(1)

    def _read_reg(self, register):
        self.cs.value(0)
        self.spi.write(bytes([register & 0x7f]))
        response = self.spi.read(1)
        self.cs.value(1)
        return response[0]

    def init(self):
        """
        Initialize the radio with the given parameters.
        """
        # Set frequency
        self.set_frequency(self.parameters['frequency'])

        # Set LoRa mode and other registers
        self._write_reg(self.REG_OP_MODE, self.MODE_LONG_RANGE_MODE)
        self._write_reg(self.REG_FIFO_TX_BASE_ADDR, 0)
        self._write_reg(self.REG_FIFO_RX_BASE_ADDR, 0)
        self._write_reg(self.REG_LNA, self._read_reg(self.REG_LNA) | 0x03)
        self._write_reg(self.REG_MODEM_CONFIG_3, 0x04) # AGC Auto On
        self.set_tx_power(self.parameters.get('tx_power_level', 17))
        self.standby()

    def set_frequency(self, frequency):
        freq = int((frequency * 1e6) / self.FREQ_STEP)
        self._write_reg(self.REG_FRF_MSB, (freq >> 16) & 0xFF)
        self._write_reg(self.REG_FRF_MID, (freq >> 8) & 0xFF)
        self._write_reg(self.REG_FRF_LSB, freq & 0xFF)

    def set_tx_power(self, level):
        # PA_BOOST pin
        self._write_reg(self.REG_PA_CONFIG, 0x80 | (level - 2))

    def standby(self):
        self._write_reg(self.REG_OP_MODE, self.MODE_LONG_RANGE_MODE | self.MODE_STDBY)

    def sleep(self):
        self._write_reg(self.REG_OP_MODE, self.MODE_LONG_RANGE_MODE | self.MODE_SLEEP)

    def send(self, data):
        """
        Send a packet.
        """
        self.standby()
        self._write_reg(self.REG_FIFO_ADDR_PTR, 0)
        self._write_reg(self.REG_PAYLOAD_LENGTH, len(data))

        # Write data to FIFO
        for b in data:
            self._write_reg(self.REG_FIFO, b)

        # Set to transmit mode
        self._write_reg(self.REG_OP_MODE, self.MODE_LONG_RANGE_MODE | self.MODE_TX)

        # Wait for TX done
        while (self._read_reg(self.REG_IRQ_FLAGS) & self.IRQ_TX_DONE_MASK) == 0:
            time.sleep_ms(10)

        # Clear IRQ flags
        self._write_reg(self.REG_IRQ_FLAGS, self.IRQ_TX_DONE_MASK)

    def receive(self):
        """
        Set receive mode.
        """
        self._write_reg(self.REG_OP_MODE, self.MODE_LONG_RANGE_MODE | self.MODE_RX_CONTINUOUS)

    def on_receive(self, callback):
        """
        Set the on-receive callback.
        """
        self.dio0.irq(trigger=Pin.IRQ_RISING, handler=callback)

    def received_packet(self):
        """
        Check if a packet has been received.
        """
        irq_flags = self._read_reg(self.REG_IRQ_FLAGS)
        
        # Clear IRQ flags
        self._write_reg(self.REG_IRQ_FLAGS, irq_flags)

        if (irq_flags & self.IRQ_RX_DONE_MASK) and \
           (irq_flags & self.IRQ_PAYLOAD_CRC_ERROR_MASK) == 0:
            return True
        return False
        
    def read_payload(self):
        """
        Read the payload of a received packet.
        """
        # Set FIFO address pointer to current RX address
        self._write_reg(self.REG_FIFO_ADDR_PTR, self._read_reg(self.REG_FIFO_RX_CURRENT_ADDR))

        # Read payload length
        payload_length = self._read_reg(self.REG_RX_NB_BYTES)

        # Read payload
        payload = bytearray()
        for _ in range(payload_length):
            payload.append(self._read_reg(self.REG_FIFO))

        return bytes(payload)

    def get_pkt_snr_value(self):
        """
        Get the SNR of the last received packet.
        """
        snr = self._read_reg(self.REG_PKT_SNR_VALUE)
        return snr / 4

    def get_pkt_rssi_value(self):
        """
        Get the RSSI of the last received packet.
        """
        rssi = self._read_reg(self.REG_PKT_RSSI_VALUE)
        return rssi - (164 if self.parameters['frequency'] < 868 else 157)