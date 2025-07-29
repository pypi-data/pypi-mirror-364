from .serial_device import SerialDevice
from .device_config import DEVICE_CONFIG

def load_device_classes(config=DEVICE_CONFIG):
    """Dynamically generate device classes from the Python configuration."""
    device_classes = {}
    for device in config:
        class_name = device["name"]
        cls = create_device_class(
            class_name,
            device["vidpids"],
            device.get("default_baudrate", 9600),
            device.get("default_timeout", 2)
        )
        device_classes[class_name] = cls

    return device_classes

def create_device_class(name, vidpids, default_baudrate, default_timeout):
    """Create a device class dynamically."""
    cls = type(
        name,
        (SerialDevice,),
        {
            "VIDPIDS": vidpids,
            "__init__": create_init(default_baudrate, default_timeout)
        }
    )
    return cls

def create_init(default_baudrate, default_timeout):
    """Create the __init__ method dynamically for each class."""
    def __init__(self, port=None, baudrate=None, timeout=None, read_size=1, data_handler=None, on_connected=None, on_disconnected=None):
        baudrate = baudrate or default_baudrate
        timeout = timeout or default_timeout

        # Initialize the parent class
        super(self.__class__, self).__init__(
            vidpid=self.VIDPIDS,
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            read_size=read_size,
            data_handler=data_handler,
            on_connected=on_connected,
            on_disconnected=on_disconnected
        )
    return __init__

def register_device(name, vidpids, default_baudrate=9600, default_timeout=2):
    """Register a new device class dynamically."""
    cls = create_device_class(name, vidpids, default_baudrate, default_timeout)
    globals()[name] = cls  # Make the class available globally
    return cls

# Load device classes from the configuration and register them
device_classes = load_device_classes()
globals().update(device_classes)
