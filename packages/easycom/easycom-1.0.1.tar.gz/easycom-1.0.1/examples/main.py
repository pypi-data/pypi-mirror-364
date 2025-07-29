# examples/main.py

from easycom.devices import Arduino
import struct

def handle_data(data):
    """Callback function to handle incoming data."""
    value = struct.unpack("<B", data)[0]
    print(f"Received: {value}")

# Initialize Arduino (auto-detect)
arduino = Arduino(read_size=1, data_handler=handle_data)

# Send data to the device
arduino.write(b'Hello')

try:
    while True:
        pass  # Keep the main thread running
except KeyboardInterrupt:
    arduino.disconnect()
