import serial.tools.list_ports
import logging

logger = logging.getLogger(__name__)


def detect_ports(vidpid_list=None):
    """Detect available serial ports based on VID/PIDs."""
    matched_ports = []
    for port in serial.tools.list_ports.comports():
        if vidpid_list and any(vidpid.lower() in port.hwid.lower() for vidpid in vidpid_list):
            logger.info(f"Found device at {port.device}")
            matched_ports.append(port.device)
    return matched_ports
