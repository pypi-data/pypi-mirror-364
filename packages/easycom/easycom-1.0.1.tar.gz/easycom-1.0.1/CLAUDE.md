# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EasyCom is a Python library for asynchronous serial communication with USB UART devices (Arduino, ESP32, Raspberry Pi Pico, etc.). The library provides non-blocking communication, automatic port detection and reconnection, and dynamic device registration.

## Development Commands

### Building and Distribution
```bash
# Build the package
python -m build

# Install in development mode
pip install -e .

# Install from built package
pip install dist/easycom-*.whl
```

### Running Examples
```bash
# Run the main example
python examples/main.py
```

## Code Architecture

### Core Components

**`easycom/serial_device.py`** - Base `SerialDevice` class that handles:
- Threaded communication (separate read/write threads)
- Automatic port detection and reconnection
- Queue-based thread-safe writes
- Connection management and error handling
- Optional connection/disconnection callbacks with default implementations

**`easycom/devices.py`** - Dynamic device class generation:
- Creates device classes from configuration at runtime
- Provides `register_device()` function for adding custom devices
- Loads all predefined device classes into global namespace

**`easycom/device_config.py`** - Device configuration data containing VID/PID mappings, default baudrates, and timeouts for 17+ supported devices

**`easycom/utils.py`** - Port detection utilities using pyserial to match devices by VID/PID

### Architecture Pattern

The library uses a dynamic class generation pattern where device classes (Arduino, ESP32, etc.) are created at runtime from configuration data. Each device class inherits from `SerialDevice` and gets specific VID/PIDs and defaults.

Device communication happens through three threads:
1. Main thread - handles port detection and connection management
2. Read thread - continuously reads data from device
3. Write thread - processes queued write operations

### Key Dependencies

- `pyserial` - Serial communication
- `threading` - Asynchronous communication
- `queue` - Thread-safe data passing

## Important Implementation Details

- All device classes are dynamically generated from `DEVICE_CONFIG` at import time
- The `SerialDevice` base class automatically starts its thread on initialization
- Port detection uses VID/PID matching against `serial.tools.list_ports`
- Write operations are queued and processed asynchronously
- Connection failures trigger automatic reconnection attempts
- Data handling is customizable via callback functions
- Connection and disconnection events can be handled with optional callbacks (`on_connected`, `on_disconnected`)