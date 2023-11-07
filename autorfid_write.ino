#include <MFRC522.h>
#include <SPI.h>
#include <string.h>

#define RESET_PIN 5
#define SS_PIN 10

MFRC522 rfid(SS_PIN, RESET_PIN);
MFRC522::MIFARE_Key key;
char firstPartHash[17];
char secondPartHash[17];

void serialEvent()
{
    while (Serial.available())
    {
        char hash[33];
        int bytesRead = Serial.readBytesUntil('\n', hash, sizeof(hash));

        Serial.println(hash);
        hash[bytesRead] = '\0';
        // First part of the hash.
        memcpy(firstPartHash, hash, sizeof(firstPartHash) - 1);
        memcpy(secondPartHash, hash + sizeof(firstPartHash) - 1, sizeof(secondPartHash) - 1);

        // Null-termination of secondPart of the hash.
        firstPartHash[sizeof(firstPartHash) - 1] = '\0';
        secondPartHash[sizeof(secondPartHash) - 1] = '\0';
        // READ CARD
        Serial.println("Put your card.");
    }
}

void setup()
{
    Serial.begin(115200);
    SPI.begin();

    while (!Serial)
        ;

    rfid.PCD_Init();
    // Set Key
    for (int i = 0; i < MFRC522::MF_KEY_SIZE; i++)
    {
        key.keyByte[i] = 0xFF; // 6 bytes 0xFF as key
    }

    Serial.println("Waiting for the data...");
    delay(100);
}

void loop()
{
    MFRC522::StatusCode status;
    if (firstPartHash[0] != '\0' || secondPartHash[0] != '\0')
    {
        byte sector = 1;
        byte firstHashBlockAddress = 4;
        byte secondHashBlockAddress = 5;

        byte firstHashByte[16];
        byte secondHashByte[17];

        byte buffer[18];
        byte bufferSize = sizeof(buffer);

        // We need to convert the first and the second part of the hash from char array to byte.
        uint8_t firstHash;
        uint8_t secondHash;
        for (int i = 0; i < 16; i++)
        {
            firstHashByte[i] = firstPartHash[i];
            secondHashByte[i] = secondPartHash[i];
        }


        if (!rfid.PICC_IsNewCardPresent())
        {
            return;
        }

        if (!rfid.PICC_ReadCardSerial())
        {
            return;
        }

        status = rfid.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, firstHashBlockAddress, &key, &(rfid.uid));
        if (status == MFRC522::STATUS_OK)
        {
            Serial.println("Writing data in Block 4");
            status = (MFRC522::StatusCode)rfid.MIFARE_Write(firstHashBlockAddress, firstHashByte, 16);
            if (status == MFRC522::STATUS_OK)
            {
                Serial.println(firstHash);
                Serial.println("Block 4 Write Success!");
            }

            Serial.println("Writing data in Block 5");
            status = (MFRC522::StatusCode)rfid.MIFARE_Write(secondHashBlockAddress, secondHashByte, 16);
            if (status == MFRC522::STATUS_OK)
            {
                Serial.println("Block 5 Write Success!");
            }

            // * READ BLOCK 4
            status = (MFRC522::StatusCode) rfid.MIFARE_Read(firstHashBlockAddress, buffer, &bufferSize);
            if (status != MFRC522::STATUS_OK) {
                Serial.print("MIFARE_Read() failed: ");
                Serial.println(status);
            }

            Serial.println("Block 4:");
            dumpByteArray(buffer, bufferSize - 2);
            Serial.println();
            Serial.println("Compare data if same:");
            byte block4Count = 0;
            for (int i = 0; i < 16; i++) {
                if (buffer[i] != firstHashByte[i]) {
                    Serial.println("Block 4 is not the same");
                    return;
                } else {
                    block4Count++;
                }
            }
            if (block4Count == 16) {
                Serial.println("Block 4 is the same");
            }
            
            // * READ BLOCK 5
            status = (MFRC522::StatusCode) rfid.MIFARE_Read(secondHashBlockAddress, buffer, &bufferSize);
            if (status != MFRC522::STATUS_OK) {
                Serial.print("MIFARE_Read() failed: ");
                Serial.println(status);
            }

            byte block5Count = 0;
            for (int i = 0; i < 16; i++) {
                if (buffer[i] != secondHashByte[i]) {
                    Serial.println("Block 5 is not the same");
                    return;
                } else {
                    block5Count++;
                }
            }
            if (block5Count == 16) {
                Serial.println("Block 5 is the same");
            }

            Serial.println("Block 5:");
            dumpByteArray(buffer, bufferSize - 2);

            Serial.println("Ready for another write");
            memset(firstPartHash, 0, sizeof(firstPartHash));
            memset(secondPartHash, 0, sizeof(secondPartHash));
        }

        rfid.PICC_HaltA();
        rfid.PCD_StopCrypto1();

        return;
    }
}

void dumpByteArray(byte *buffer, byte bufferSize) {
    for (byte i = 0; i < bufferSize; i++) {
        Serial.print(buffer[i] < 0x10 ? " 0" : " ");
        Serial.print(buffer[i], HEX);
    }
}