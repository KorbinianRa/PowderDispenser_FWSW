#include "Comms.h"

// Static member variables
char Comms::inputBuffer[Comms::buffSize] = {0};  // Buffer to store incoming data from the PC.
unsigned long Comms::curMillis = 0;             // Tracks the current time in milliseconds.
unsigned long Comms::prevReplyToPCmillis = 0;   // Tracks the last time a reply was sent to the PC.
unsigned long Comms::replyToPCinterval = 1000;  // Interval (in milliseconds) for sending periodic replies to the PC.

/**
 * Constructor for the Comms class.
 * 
 * Initializes references to utility, scale, mixer, and dispenser control objects.
 * Parameters:
 * - `utils` (Utils&): Reference to the utility class for shared functionality.
 * - `scaleControls` (ScaleControls&): Reference to the scale control object.
 * - `mixerControls` (MixerControls&): Reference to the mixer control object.
 * - `dispenserControls` (DispenserControls&): Reference to the dispenser control object.
 */
Comms::Comms(Utils& utils, ScaleControls& scaleControls, MixerControls& mixerControls, DispenserControls& dispenserControls)
    : utils(utils), scaleControls(scaleControls), mixerControls(mixerControls), dispenserControls(dispenserControls) {}

/**
 * Reads data from the PC over Serial.
 * 
 * Behavior:
 * - Processes incoming characters and stores them in the `inputBuffer`.
 * - Recognizes the start and end markers to determine when a complete command is received.
 * - Calls `parseData()` to process the received command.
 */
void Comms::getDataFromPC() {
    while (Serial.available() > 0) {  // Check if data is available on the Serial port.
        char x = Serial.read();      // Read one character at a time.
        if (bytesRecvd < buffSize - 1) {
            if (x == endMarker) {  // End of command detected.
                readInProgress = false;
                newDataFromPC = true;
                inputBuffer[bytesRecvd] = 0;  // Null-terminate the string.
                parseData();  // Process the complete command.
            } else if (readInProgress) {  // Continue reading the command.
                inputBuffer[bytesRecvd++] = x;
            } else if (x == startMarker) {  // Start of command detected.
                bytesRecvd = 0;
                readInProgress = true;
            }
        } else {
            bytesRecvd = buffSize - 1;  // Prevent buffer overflow.
        }
    }
}

/**
 * Sends a reply message back to the PC.
 * 
 * Behavior:
 * - Includes the last received command and the current time (shifted for reduced resolution).
 * - Only sends a reply if there is new data from the PC.
 */
void Comms::replyToPC() {
    if (newDataFromPC) {
        newDataFromPC = false;  // Reset the new data flag.
        Serial.print("<Msg ");  // Start the reply message.
        Serial.print(messageFromPC);  // Include the received message.
        Serial.print(" Time ");
        Serial.print(curMillis >> 9);  // Shifted current time for reduced resolution.
        Serial.println(">");  // End the reply message.
    }
}

/**
 * Parses and processes the command received from the PC.
 * 
 * Behavior:
 * - Splits the command string using commas as delimiters.
 * - Matches the first token to a known command and executes the corresponding action.
 * - Commands include operations for mixing, draining, dispensing, and controlling the scale.
 */
void Comms::parseData() {
    strcpy(messageFromPC, inputBuffer);  // Copy the input buffer for message storage.
    char *token = strtok(inputBuffer, ",");  // Extract the first token (command).

    // Compare the command token and execute the corresponding operation.
    if (strcmp(token, "Mix") == 0) {
        float duration = atof(strtok(NULL, ","));  // Get duration from the command.
        mixerControls.run(mixerControls.getMixerRelay(), duration);
        replyToPC();
    } else if (strcmp(token, "Drain") == 0) {
        float duration = atof(strtok(NULL, ","));  // Get duration for draining.
        mixerControls.run(mixerControls.getDrainRelay(), duration);
        replyToPC();
    } else if (strcmp(token, "Pump") == 0) {
        int pin = atoi(strtok(NULL, ","));         // Get pin number.
        float duration = atof(strtok(N
