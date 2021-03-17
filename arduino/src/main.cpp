#include "Arduino.h"

#define SER 2
#define SRCLK 3
#define RCLK 4
#define EEPROM_IO0 5
#define EEPROM_IO7 12
#define EEPROM_WE 13

#define READ_CMD 0x3f
#define WRITE_CMD 0x4f

void setAddress(int address, bool outputEnable) {
    digitalWrite(RCLK, LOW);
    digitalWrite(SRCLK, LOW);

    shiftOut(SER, SRCLK, MSBFIRST, (address >> 8) | (outputEnable ? 0x00 : 0x80));
    shiftOut(SER, SRCLK, MSBFIRST, address);

    digitalWrite(RCLK, HIGH);
    digitalWrite(RCLK, LOW);
}

byte readEeprom(int address) {
    for (int pin = EEPROM_IO0; pin <= EEPROM_IO7; ++pin) {
        pinMode(pin, INPUT);
    }
    setAddress(address, true);

    byte data = 0;
    for (int pin = EEPROM_IO7; pin >= EEPROM_IO0; --pin) {
        data = (data << 1) | digitalRead(pin);
    }
    return data;
}

void writeEeprom(int address, byte data) {
    setAddress(address, false);
    int lastbit;
    for (int pin = EEPROM_IO0; pin <= EEPROM_IO7; ++pin) {
        pinMode(pin, OUTPUT);
        lastbit = data & 1;
        digitalWrite(pin, lastbit);
        data >>= 1;
    }
    digitalWrite(EEPROM_WE, LOW);
    delayMicroseconds(1);
    digitalWrite(EEPROM_WE, HIGH);

    // write cycle is finished when IO7 shows the correct data
    for (int pin = EEPROM_IO0; pin <= EEPROM_IO7; ++pin) {
        pinMode(pin, INPUT);
    }
    setAddress(address, true);
    while (digitalRead(EEPROM_IO7) != lastbit) delayMicroseconds(1);
}

void printContents() {
    for (int addr = 0; addr < 2048; addr += 16) {
        byte data[16];
        for (int offset = 0; offset < 16; offset++) {
            data[offset] = readEeprom(addr+offset);
        }

        char buf[80];
        sprintf(buf,
                "%03x:  %02x %02x %02x %02x %02x %02x %02x %02x   "
                "%02x %02x %02x %02x %02x %02x %02x %02x",
                addr,
                data[0], data[1], data[2], data[3],
                data[4], data[5], data[6], data[7],
                data[8], data[9], data[10], data[11],
                data[12], data[13], data[14], data[15]);
        Serial.println(buf);
    }
}

void eraseEeprom() {
    for (int addr = 0; addr < 2048; addr++) {
        writeEeprom(addr, 0xff);
    }
}

void writeIncoming() {
    uint8_t incoming;

    for (int addr = 0; addr < 2048; addr++) {
        while (!Serial.available()) delayMicroseconds(1);
        incoming = Serial.read();
        writeEeprom(addr, incoming);
        Serial.write(incoming);
    }
}

void echoContents() {
    uint8_t content;
    for (int addr = 0; addr < 2048; addr++) {
        content = readEeprom(addr);
        Serial.write(content);
    }
    Serial.flush();
}

void setup()
{
    uint8_t incoming;

    pinMode(SER, OUTPUT);
    pinMode(SRCLK, OUTPUT);
    pinMode(RCLK, OUTPUT);
    digitalWrite(EEPROM_WE, HIGH);
    pinMode(EEPROM_WE, OUTPUT);

    Serial.begin(57600);

    while (1) {
        while (!Serial.available()) delayMicroseconds(1);
        incoming = Serial.read();
        Serial.write(incoming);
        break;
    }
    if (incoming == WRITE_CMD) {
        writeIncoming();
    }
    echoContents();
}

void loop()
{
}
