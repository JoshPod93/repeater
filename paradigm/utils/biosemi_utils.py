"""
Biosemi utilities for EEG trigger communication.
EXACT COPY from grasp/paradigm/paradigm_utils.py

Handles serial port communication with Biosemi hardware for sending triggers
to the EEG data stream.

Author: A. Tates (JP)
BCI-NE Lab, University of Essex
Date: January 26, 2026
"""

import serial
import time
import warnings
from typing import Optional

# Global serial port instance
_serial_port = None

# Track trigger sending failures (for end-of-block reporting)
_trigger_failures = []


def get_default_port():
    """Get the default COM port for this system.
    
    Checks environment variable BIOSEMI_PORT first, then falls back to platform-specific default.
    """
    import os
    # Check environment variable first (allows per-machine configuration)
    env_port = os.environ.get('BIOSEMI_PORT')
    if env_port:
        return env_port
    
    # Platform-specific defaults
    import platform
    if platform.system() == 'Windows':
        return 'COM4'  # Common Windows default
    else:
        return '/dev/ttyUSB0'  # Common Linux default


def open_serial_port(port=None, baudrate=115200):
    """
    Open and return a persistent serial port connection.
    EXACT COPY from grasp/paradigm/paradigm_utils.py
    
    Args:
        port (str): COM port to use (default: from get_default_port())
        baudrate (int): Baud rate (default: 115200)
    
    Returns:
        serial.Serial: Opened serial port object, or None if failed
    """
    global _serial_port
    
    if port is None:
        port = get_default_port()
    
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
        
        print(f"Serial port {port} opened successfully (buffers cleared)")
        return _serial_port
    except Exception as e:
        print(f"Error opening serial port {port}: {e}")
        return None


def close_serial_port(block_folder_path=None):
    """Close the persistent serial port connection.
    EXACT COPY from grasp/paradigm/paradigm_utils.py
    
    Args:
        block_folder_path (str, optional): Path to block folder for saving trigger failure log
    """
    global _serial_port
    
    if _serial_port is None or not _serial_port.is_open:
        return
    
    try:
        # Reset output buffer before closing
        _serial_port.reset_output_buffer()
        _serial_port.flush()
        
        # Close the port
        _serial_port.close()
        print("Serial port closed")
        
        # Report trigger failures if any
        if _trigger_failures:
            print(f"\n⚠️  WARNING: {len(_trigger_failures)} trigger(s) failed during this block:")
            for failure in _trigger_failures:
                print(f"   - {failure['marker']} (value {failure['value']}) at {failure['time']:.2f}s")
            
            # Optionally save to file
            if block_folder_path:
                try:
                    import os
                    failure_log_path = os.path.join(block_folder_path, 'trigger_failures.txt')
                    with open(failure_log_path, 'w') as f:
                        f.write(f"Trigger Failures Report\n")
                        f.write(f"Total failures: {len(_trigger_failures)}\n\n")
                        for failure in _trigger_failures:
                            f.write(f"{failure['marker']} (value {failure['value']}) at {failure['time']:.2f}s\n")
                    print(f"   Failure log saved to: {failure_log_path}")
                except Exception as e:
                    print(f"   Could not save failure log: {e}")
            
            # Clear failures list
            _trigger_failures.clear()
        
    except Exception as e:
        print(f"Error closing serial port: {e}")
    
    _serial_port = None


def _send_eeg_trigger(marker_value, marker_name=None):
    """
    Send a trigger byte via the already-open serial port.
    EXACT COPY from grasp/paradigm/paradigm_utils.py
    
    Much faster than opening/closing for each trigger.
    
    Buffer Management:
    - flush() is called after write() to ensure immediate transmission
    - This flushes: Python pyserial buffer → OS serial driver buffer → USB chip buffer
    - Without flush(), bytes may be buffered and sent in batches, causing timing issues
    - flush() overhead is minimal (<0.1ms) compared to the 5ms delay in send_biosemi_trigger()
    
    Args:
        marker_value (int): Trigger value (0-255)
        marker_name (str): Human-readable name for logging
    """
    global _serial_port
    
    if _serial_port is None or not _serial_port.is_open:
        # CRITICAL: Don't silently fail - this indicates a serious problem
        error_msg = f"Serial port not open. Call open_serial_port() first. Attempted to send trigger {marker_value} ({marker_name})"
        warnings.warn(error_msg)
        return False
    
    try:
        # Send the marker value as a single byte
        _serial_port.write(bytes([marker_value]))
        _serial_port.flush()  # CRITICAL: Ensure immediate transmission to prevent buffering

        return True

    except Exception as e:
        warnings.warn(f"Could not send marker via serial port: {e}")
        return False


def send_biosemi_trigger(trigger_code: int, marker_name: Optional[str] = None) -> bool:
    """
    Send trigger byte to Biosemi via serial port.
    Uses same implementation style as reference project.
    
    Critical steps (same as reference):
    1. Write trigger byte (via _send_eeg_trigger)
    2. Flush immediately (prevents buffering) - done in _send_eeg_trigger
    3. Wait 5ms (prevents rapid-fire errors) - done here
    
    Buffer Management:
    - flush() is called after write() to ensure immediate transmission
    - This flushes: Python pyserial buffer → OS serial driver buffer → USB chip buffer
    - Without flush(), bytes may be buffered and sent in batches, causing timing issues
    - The 5ms delay prevents rapid-fire trigger errors that Biosemi hardware can't handle
    
    Note: The 5ms delay is critical for BioSemi hardware to properly register each trigger.
    Without proper spacing, triggers can be dropped or corrupted, especially when sent
    in rapid succession.
    
    Parameters
    ----------
    trigger_code : int
        Trigger code to send (0-255) - uses OUR experiment's codes
    marker_name : str, optional
        Human-readable name for logging
    
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    # Validate trigger code range
    if trigger_code < 0 or trigger_code > 255:
        warnings.warn(f"Trigger code {trigger_code} out of range (0-255)")
        return False
    
    # Send to EEG hardware (same implementation style as reference)
    send_success = _send_eeg_trigger(trigger_code, marker_name)
    
    if not send_success:
        return False
    
    # Add 5ms delay to prevent trigger dropping due to rapid hardware timing
    # This delay is critical for BioSemi hardware to properly register each trigger
    time.sleep(0.005)
    
    return True


# Compatibility aliases (for existing code)
def connect_biosemi(port: str = None, baudrate: int = 115200) -> serial.Serial:
    """Alias for open_serial_port() for compatibility."""
    return open_serial_port(port=port, baudrate=baudrate)


def verify_biosemi_connection(connection: serial.Serial) -> bool:
    """Verify Biosemi connection is active and ready."""
    if connection is None:
        return False
    try:
        return connection.is_open
    except Exception:
        return False


def close_biosemi_connection(connection: Optional[serial.Serial] = None):
    """Alias for close_serial_port() for compatibility."""
    close_serial_port()


