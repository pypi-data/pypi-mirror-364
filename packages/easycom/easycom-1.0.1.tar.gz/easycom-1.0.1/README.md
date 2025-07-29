# EasyCom

**EasyCom** is a Python library designed for **asynchronous serial communication** with USB UART devices such as **Arduino, ESP32, Raspberry Pi Pico, Teensy**, and others. With **non-blocking communication**, **automatic port detection and reconnection**, and an **easy-to-use API**, EasyCom allows you to seamlessly interact with multiple devices. It also supports the **dynamic registration of new devices** at runtime.

---

## Features

- **Asynchronous Communication**: Uses threading to provide non-blocking read and write operations.
- **Automatic Port Detection and Reconnection**: Matches devices using VID/PID for automatic connection and reconnection if disconnected.
- **Pre-configured and Dynamically Registered Devices**: Built-in support for common devices, with the ability to add custom devices dynamically.
- **Thread-safe Writes**: Queue-based data management ensures safe, consistent writes.
- **Customizable Data Handlers**: Process incoming data using custom callback functions for maximum flexibility.

---

## Installation

You can install EasyCom directly with pip:

```bash
pip install easycom
```

---

## Getting Started

### Basic Example: Arduino with Default Parameters

This example demonstrates setting up an **Arduino** device using default parameters. With **automatic port detection**, the library will attempt to connect to the first available port with matching VID/PID.

```python
from easycom.devices import Arduino

# Define a simple callback function to handle received data
def handle_data(data):
    print(f"Received: {data}")

# Initialize Arduino with automatic port detection and default settings
arduino = Arduino(data_handler=handle_data)

# Keep the program running to receive data
input("Press Enter to disconnect...")

# Disconnect the Arduino
arduino.disconnect()
```

---

### Overriding Parameters

EasyCom allows you to override specific parameters such as `port`, `baudrate`, `timeout`, and `data_handler`. Each example below illustrates how to set these parameters.

#### 1. Overriding the `port`

If the device is connected to a specific port, you can set it explicitly:

```python
arduino = Arduino(port="/dev/ttyUSB0", data_handler=handle_data)
```

#### 2. Overriding the `baudrate`

To customize the baud rate (e.g., 115200), set it during initialization:

```python
arduino = Arduino(baudrate=115200, data_handler=handle_data)
```

#### 3. Overriding the `timeout`

Adjust the timeout (in seconds) for read and write operations:

```python
arduino = Arduino(timeout=5, data_handler=handle_data)
```

Here’s an updated example using a `struct` in C++ on the Arduino side to send an integer and a float together as a single binary package. This structure will match the Python `struct` for decoding.

---

#### 4. Using a `struct`-based Data Handler

In this example, we’ll send data as a structured binary package from Arduino and parse it in Python using the `struct` module. The Arduino will send an integer and a float in one structured transmission.

```python
import struct
from easycom.devices import Arduino

# Define a data handler to parse binary data
def handle_data(data):
    # Parse data as an integer and a float
    parsed_data = struct.unpack("<if", data)  # "<if" represents little-endian int, float
    print(f"Parsed Data: Integer={parsed_data[0]}, Float={parsed_data[1]}")

# Initialize the Arduino device
arduino = Arduino(data_handler=handle_data)
```

##### Arduino Code with C++ Struct

On the Arduino, we’ll define a C++ `struct` to hold the data, then send this struct as binary data.

```cpp
// Arduino code to send a struct with an integer and a float as binary data over Serial

struct DataPacket {
  int myInt;
  float myFloat;
};

// Create an instance of the struct and populate it
DataPacket packet = {42, 3.14};

void setup() {
  Serial.begin(9600);  // Ensure this matches the baud rate in EasyCom
}

void loop() {
  // Send the struct as binary data
  Serial.write((byte*)&packet, sizeof(packet));  // Send entire struct as binary

  delay(1000);  // Send data every second
}
```

In this code:
- We define a `DataPacket` struct containing an integer (`myInt`) and a float (`myFloat`).
- `Serial.write((byte*)&packet, sizeof(packet));` sends the entire struct as a single binary transmission.
- The data format sent by Arduino matches `struct.unpack("<if", data)` on the Python side, where:
  - `"<if"` specifies little-endian format: an integer (`i`) followed by a float (`f`).

This setup allows Python to parse the binary data from Arduino, resulting in correctly structured data for your application.

#### 5. Using Connection and Disconnection Callbacks

You can specify custom callbacks to handle connection and disconnection events:

```python
def on_device_connected(port):
    print(f"Device connected to {port}")

def on_device_disconnected(port):
    print(f"Device disconnected from {port}")

arduino = Arduino(
    data_handler=handle_data,
    on_connected=on_device_connected,
    on_disconnected=on_device_disconnected
)
```

#### 6. Combining All Parameter Overrides

You can combine multiple overrides, specifying `port`, `baudrate`, `timeout`, callbacks, and a custom `data_handler`.

```python
arduino = Arduino(
    port="/dev/ttyUSB0",
    baudrate=115200,
    timeout=3,
    data_handler=handle_data,
    on_connected=on_device_connected,
    on_disconnected=on_device_disconnected
)
```

---

### Registering a New Device at Runtime

To add a new device dynamically, use `register_device`. The example below registers a custom device `MyDevice` with a unique VID/PID, baud rate, and timeout.

```python
from easycom.devices import register_device

# Register a custom device class
MyDevice = register_device(
    name="MyDevice",
    vidpids=["1234:5678"],
    default_baudrate=57600,
    default_timeout=4
)

# Initialize and use the custom device
device = MyDevice(data_handler=handle_data)
device.write(b"Hello, MyDevice!")
device.disconnect()
```

---

## Supported Devices

EasyCom includes pre-configured support for several common USB UART devices. 

| **Device**        | **VID/PIDs**                    | **Default Baudrate** | **Default Timeout** |
|-------------------|----------------------------------|----------------------|---------------------|
| Arduino           | 2341:0043, 2341:0010, 0403:6001 | 9600                 | 2                   |
| Raspberry Pi Pico | 2E8A:0005                       | 115200               | 2                   |
| Teensy            | 16C0:0483, 16C0:0487            | 9600                 | 2                   |
| ESP32             | 10C4:EA60, 1A86:7523            | 115200               | 3                   |
| STM32             | 0483:5740                       | 9600                 | 2                   |
| CP210x            | 10C4:EA60                       | 115200               | 2                   |
| FTDI              | 0403:6001, 0403:6015            | 9600                 | 2                   |
| CH340             | 1A86:7523                       | 9600                 | 3                   |
| Prolific          | 067B:2303                       | 9600                 | 2                   |
| RaspberryPi       | 2E8A:000A                       | 115200               | 2                   |
| NRF52840          | 1915:520A                       | 115200               | 2                   |
| MCP2200           | 04D8:00DD                       | 9600                 | 2                   |
| EFM32             | 10C4:E005                       | 115200               | 2                   |
| STLink            | 0483:374B                       | 9600                 | 2                   |
| FT232H            | 0403:6015                       | 3000000              | 2                   |
| FX2LP             | 04B4:8613                       | 9600                 | 2                   |
| LPC11Uxx          | 1FC9:009C                       | 115200               | 2                   |


### Adding Additional Devices

You can extend this list by registering additional devices with `register_device`, as shown in the example above.

---

## Advanced Features

### Automatic Reconnection

If a device disconnects, EasyCom will attempt to reconnect automatically, simplifying communication in environments where devices are intermittently connected.

### Debug Logging

Enable detailed logging to trace communication flow and troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Common Usage Patterns

### Continuous Data Handling

For applications requiring continuous data reading, the following setup ensures the program stays open until manually closed:

```python
from easycom.devices import Arduino

def handle_data(data):
    print(f"Data Received: {data}")

arduino = Arduino(data_handler=handle_data)

try:
    while True:
        pass  # Keep the program running to process data
except KeyboardInterrupt:
    print("Disconnecting...")
    arduino.disconnect()
```

### Sending Data Periodically

To send data at regular intervals, use a loop with a delay, allowing the program to handle data without blocking other operations.

```python
import time

while True:
    arduino.write(b"Ping")
    time.sleep(1)
```

---

## License

EasyCom is available under the **MIT License**.

---

## Contributing

Contributions are welcome! Please submit issues or pull requests on GitLab to help improve EasyCom.

---

## Resources

- **Source Code**: [GitLab Repository](https://gitlab.com/acemetrics-technologies/easycom)  
- **Issue Tracker**: [Report Issues](https://gitlab.com/acemetrics-technologies/easycom/-/issues)

---

## Authors

- **Acemetrics Technologies**  
  [vishnu@acemetrics.com](mailto:vishnu@acemetrics.com)

---

## Summary

**EasyCom** simplifies working with USB UART devices, providing reliable, non-blocking communication, automatic port detection and reconnection, and dynamic device registration for fast, flexible interaction with serial devices.