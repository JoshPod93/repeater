"""
Biosemi utilities for EEG trigger communication.

Handles serial port communication with Biosemi hardware for sending triggers
to the EEG data stream. Based on patterns from grasp/paradigm project.

Author: A. Tates (JP)
BCI-NE Lab, University of Essex
Date: January 26, 2026
"""

import serial
import time
import warnings
from typing import Optional

# Global serial port instance (similar to grasp/paradigm pattern)
_serial_port = None


def connect_biosemi(port: str = 'COM3', baudrate: int = 115200) -> serial.Serial:
    """
    Open serial port connection to Biosemi hardware.
    
    Opens port with 8N1 configuration (8 data bits, no parity, 1 stop bit).
    Clears input/output buffers immediately after opening to prevent stale data.
    
    Parameters
    ----------
    port : str
        Serial port name (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
    baudrate : int
        Serial port baudrate (default: 115200)
    
    Returns
    -------
    serial.Serial
        Opened serial port object
    
    Raises
    ------
    Exception
        If port cannot be opened
    """
    global _serial_port
    
    try:
        _serial_port = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
            timeout=0.01
        )
        
        # CRITICAL: Clear all buffers immediately after opening to prevent stale data
        # This ensures no buffered triggers from previous sessions are sent
        _serial_port.reset_output_buffer()  # Clear output buffer
        _serial_port.flush()  # Flush any remaining data
        _serial_port.reset_input_buffer()  # Clear input buffer (if any)
        
        print(f"[BIOSEMI] Serial port {port} opened successfully (buffers cleared)")
        return _serial_port
        
    except Exception as e:
        error_msg = f"Error opening serial port {port}: {e}"
        print(f"[BIOSEMI ERROR] {error_msg}")
        raise RuntimeError(error_msg) from e


def verify_biosemi_connection(connection: serial.Serial) -> bool:
    """
    Verify Biosemi connection is active and ready.
    
    Parameters
    ----------
    connection : serial.Serial
        Serial port connection object
    
    Returns
    -------
    bool
        True if connection is valid and open, False otherwise
    """
    if connection is None:
        return False
    
    try:
        return connection.is_open
    except Exception:
        return False


def send_biosemi_trigger(connection: serial.Serial, trigger_code: int) -> bool:
    """
    Send trigger byte to Biosemi via serial port.
    
    Critical steps:
    1. Write trigger byte
    2. Flush immediately (prevents buffering)
    3. Wait 5ms (prevents rapid-fire errors)
    
    Buffer Management:
    - flush() is called after write() to ensure immediate transmission
    - This flushes: Python pyserial buffer → OS serial driver buffer → USB chip buffer
    - Without flush(), bytes may be buffered and sent in batches, causing timing issues
    - The 5ms delay prevents rapid-fire trigger errors that Biosemi hardware can't handle
    
    Parameters
    ----------
    connection : serial.Serial
        Serial port connection object
    trigger_code : int
        Trigger code to send (0-255)
    
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    if connection is None or not connection.is_open:
        warnings.warn(
            f"Serial port not open. Cannot send trigger {trigger_code}. "
            f"Call connect_biosemi() first."
        )
        return False
    
    try:
        # Validate trigger code range
        if trigger_code < 0 or trigger_code > 255:
            warnings.warn(f"Trigger code {trigger_code} out of range (0-255)")
            return False
        
        # Send the trigger value as a single byte
        connection.write(bytes([trigger_code]))
        connection.flush()  # CRITICAL: Ensure immediate transmission to prevent buffering
        
        # Wait 5ms to prevent rapid-fire trigger errors
        # This delay is critical for BioSemi hardware to properly register each trigger
        time.sleep(0.005)
        
        return True
        
    except Exception as e:
        warnings.warn(f"Could not send trigger {trigger_code} via serial port: {e}")
        return False


def close_biosemi_connection(connection: Optional[serial.Serial] = None):
    """
    Cleanly close Biosemi connection.
    
    Resets output buffer, closes port, and clears global instance.
    
    Parameters
    ----------
    connection : serial.Serial, optional
        Connection to close. If None, uses global instance.
    """
    global _serial_port
    
    # Use provided connection or global instance
    port_to_close = connection if connection is not None else _serial_port
    
    if port_to_close is not None and port_to_close.is_open:
        try:
            # Reset output buffer before closing
            port_to_close.reset_output_buffer()
            port_to_close.flush()
            
            # Close the port
            port_to_close.close()
            print("[BIOSEMI] Serial port closed")
            
        except Exception as e:
            warnings.warn(f"Error closing serial port: {e}")
    
    # Clear global instance if it was closed
    if port_to_close == _serial_port:
        _serial_port = None
