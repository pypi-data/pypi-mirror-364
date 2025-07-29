import threading
import serial
import time
from queue import Queue, Empty
import logging
from .utils import detect_ports

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SerialDevice(threading.Thread):
    """Base class for serial devices with threaded communication support."""
    
    def __init__(self, vidpid=None, port=None, baudrate=9600, timeout=2, 
                 read_size=1, data_handler=None, on_connected=None, on_disconnected=None):
        super().__init__()
        self.quit = False
        self.read_thread = None
        self.write_thread = None
        self.write_queue = Queue()
        self.vidpid = vidpid
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.read_size = read_size
        self.data_handler = data_handler
        self.on_connected = on_connected or self._default_on_connected
        self.on_disconnected = on_disconnected or self._default_on_disconnected
        self.ser = None
        self.lock = threading.Lock()
        logger.info("SerialDevice initialized.")
        self.start()

    def run(self):
        """Main thread to manage port detection and connections."""
        while not self.quit:
            if not self.port:
                logger.debug("Detecting ports...")
                ports = detect_ports(self.vidpid)
                if ports:
                    self.port = ports[0]
                    logger.info(f"Port detected: {self.port}")
                else:
                    logger.warning("No matching devices found. Retrying...")
                    time.sleep(1)
                    continue
            try:
                with serial.Serial(self.port, self.baudrate, timeout=self.timeout) as ser:
                    self.ser = ser
                    logger.info(f"Connected to {self.port}")
                    
                    # Call connection callback
                    try:
                        self.on_connected(self.port)
                    except Exception as e:
                        logger.exception(f"Error in connection callback: {e}")
                    
                    time.sleep(2)  # Allow initialization

                    # Start read and write threads
                    self.read_thread = threading.Thread(target=self.read_from_device)
                    self.write_thread = threading.Thread(target=self.write_to_device)
                    self.read_thread.start()
                    self.write_thread.start()

                    # Wait for both threads to complete or stop
                    self.read_thread.join()
                    self.write_thread.join()

                logger.info(f"Disconnected from {self.port}. Resetting port.")
                
                # Call disconnection callback
                try:
                    self.on_disconnected(self.port)
                except Exception as e:
                    logger.exception(f"Error in disconnection callback: {e}")
                
                self.port = None  # Reset port if disconnected
            except serial.SerialException as e:
                logger.error(f"Disconnected from {self.port}: {e}")
                
                # Call disconnection callback on error
                if self.port:
                    try:
                        self.on_disconnected(self.port)
                    except Exception as callback_e:
                        logger.exception(f"Error in disconnection callback: {callback_e}")
                
                self.port = None
                time.sleep(1)

    def read_from_device(self):
        """Read data from the device in a separate thread."""
        while not self.quit:
            try:
                data = self.ser.read(self.read_size)
                if data:
                    logger.info(f"Received: {data}")
                    self.handle_data(data)
            except serial.SerialException as e:
                logger.error(f"Read error: {e}")
                break

    def write_to_device(self):
        """Write data to the device in a separate thread."""
        while not self.quit:
            try:
                data = self.write_queue.get(timeout=1)  # Non-blocking with timeout
                with self.lock:
                    self.ser.write(data)
                    logger.info(f"Sent: {data}")
            except Empty:
                pass  # Continue if no data in queue
            except serial.SerialException as e:
                logger.error(f"Write error: {e}")
                break

    def write(self, data):
        """Queue data to be sent to the device."""
        logger.debug(f"Queuing data for sending: {data}")
        self.write_queue.put(data)

    def disconnect(self):
        """Stop the device communication."""
        logger.info("Disconnecting the device...")
        self.quit = True
        if self.read_thread and self.write_thread:
            self.read_thread.join()
            self.write_thread.join()
        logger.info("Device disconnected.")

    def handle_data(self, data):
        """Handle incoming data using the provided handler."""
        if callable(self.data_handler):
            try:
                logger.debug(f"Handling data: {data}")
                self.data_handler(data)
            except Exception as e:
                logger.exception(f"Error in data handler: {e}")
        else:
            logger.warning("No data handler provided.")

    def _default_on_connected(self, port):
        """Default connection callback."""
        logger.info(f"Device connected to {port}")

    def _default_on_disconnected(self, port):
        """Default disconnection callback."""
        logger.info(f"Device disconnected from {port}")
