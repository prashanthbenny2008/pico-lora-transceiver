#include <SPI.h>
#include <LoRa.h>

// --- IMPORTANT ---
// Ensure these pin definitions match your receiver's wiring!
#define SS 5
#define RST 14
#define DIO0 26

void setup() {
  Serial.begin(9600);
  while (!Serial); // Wait for serial port to connect

  Serial.println("LoRa Receiver Test");

  // Setup LoRa module
  LoRa.setPins(SS, RST, DIO0);

  // --- CRITICAL ---
  // Use the same frequency as your sender!
  if (!LoRa.begin(433E6)) {
    Serial.println("Starting LoRa failed!");
    while (1); // Halt
  }

  Serial.println("LoRa Initialized. Waiting for packets...");
}

void loop() {
  // Try to parse a packet
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // Received a packet!
    Serial.print("Received packet '");

    // Read packet
    while (LoRa.available()) {
      Serial.print((char)LoRa.read());
    }

    // Print RSSI and SNR
    Serial.print("' with RSSI ");
    Serial.print(LoRa.packetRssi());
    Serial.print(" and SNR ");
    Serial.println(LoRa.packetSnr());
  }
}