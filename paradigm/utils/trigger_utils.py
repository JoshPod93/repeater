"""
Trigger utilities for EEG synchronization.

Handles parallel port and Biosemi serial port communication for sending trigger codes to EEG systems.
Based on best practices: send trigger to EEG stream first, then log to PsychoPy.
Includes CSV mirror logging for trigger verification.
"""

from psychopy import core
from typing import Optional, Tuple, List, TYPE_CHECKING
from pathlib import Path
import csv
import logging
import time
from datetime import datetime

if TYPE_CHECKING:
    import serial

logger = logging.getLogger(__name__)


class TriggerHandler:
    """
    Handler for EEG trigger communication via parallel port and/or Biosemi serial port.
    
    Follows best practice: send trigger to EEG stream first, then log.
    Includes CSV mirror logging for trigger verification.
    
    Priority order for trigger sending:
    1. Biosemi serial port (if connected)
    2. Parallel port (if enabled)
    3. CSV logging (always)
    """
    
    def __init__(self, port_address: int = 0x0378, use_triggers: bool = False,
                 csv_log_path: Optional[Path] = None,
                 biosemi_connection: Optional['serial.Serial'] = None):
        """
        Initialize trigger handler.
        
        Parameters
        ----------
        port_address : int
            Parallel port address (default 0x0378 for LPT1)
        use_triggers : bool
            Whether to actually send triggers (False for testing)
        csv_log_path : Path, optional
            Path to CSV file for trigger logging (mirror log)
        biosemi_connection : serial.Serial, optional
            Biosemi serial port connection. If provided, triggers will be sent to Biosemi.
        """
        self.port_address = port_address
        self.use_triggers = use_triggers
        self.biosemi_connection = biosemi_connection
        self.parallel_port = None
        self.clock = core.Clock()
        self.csv_log_path = csv_log_path
        self.csv_file = None
        self.csv_writer = None
        self.trigger_log = []  # In-memory log of all triggers
        
        # Initialize CSV logging if path provided
        if self.csv_log_path is not None:
            self._init_csv_logging()
        
        # Only initialize parallel port if Biosemi is NOT available
        # (Biosemi serial port is the primary trigger method)
        if self.use_triggers and self.biosemi_connection is None:
            try:
                from psychopy import parallel
                self.parallel_port = parallel.ParallelPort(address=port_address)
                logger.info(f"Parallel port initialized at {hex(port_address)}")
            except Exception as e:
                logger.warning(f"Could not initialize parallel port: {e}. Triggers disabled.")
                self.use_triggers = False
                self.parallel_port = None
        else:
            # Biosemi is available, skip parallel port initialization
            self.parallel_port = None
    
    def _init_csv_logging(self):
        """Initialize CSV file for trigger logging."""
        try:
            # Create parent directory if needed
            self.csv_log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Open CSV file for writing
            self.csv_file = open(self.csv_log_path, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            
            # Write header
            self.csv_writer.writerow([
                'timestamp_psychopy',  # PsychoPy clock time
                'timestamp_absolute',   # Absolute datetime
                'trigger_code',         # Numeric trigger code
                'event_name',           # Human-readable event name
                'sent_to_eeg'           # Whether trigger was sent to EEG
            ])
            
            logger.info(f"CSV trigger logging initialized: {self.csv_log_path}")
        except Exception as e:
            logger.warning(f"Could not initialize CSV logging: {e}")
            self.csv_log_path = None
            self.csv_file = None
            self.csv_writer = None
    
    def send_trigger(self, trigger_code: int, hold_duration: float = 0.01,
                     event_name: Optional[str] = None) -> Tuple[float, bool]:
        """
        Send EEG trigger and return timestamp.
        
        Best practice: Send trigger to EEG stream FIRST, then log timestamp.
        This ensures EEG recording captures the trigger even if logging fails.
        
        Priority order:
        1. Biosemi serial port (if connected)
        2. Parallel port (if enabled)
        3. CSV logging (always)
        
        Parameters
        ----------
        trigger_code : int
            Trigger code to send (0-255)
        hold_duration : float
            How long to hold trigger high (seconds, default 0.01) - only for parallel port
        event_name : str, optional
            Human-readable event name for logging
        
        Returns
        -------
        timestamp : float
            Timestamp when trigger was sent
        success : bool
            Whether trigger was sent successfully
        """
        timestamp = self.clock.getTime()
        success = False
        
        # Priority 1: Send to Biosemi data stream FIRST (if connected)
        # Uses same implementation style as reference (write, flush, 5ms delay)
        # But uses OUR trigger codes directly
        if self.biosemi_connection is not None:
            try:
                from .biosemi_utils import send_biosemi_trigger
                # Send trigger directly using our codes (same implementation style as reference)
                biosemi_success = send_biosemi_trigger(trigger_code, event_name)
                if biosemi_success:
                    success = True
                    logger.debug(f"Trigger {trigger_code} ({event_name or 'unnamed'}) sent to Biosemi at {timestamp:.3f}s")
                else:
                    logger.warning(f"Failed to send trigger {trigger_code} to Biosemi")
            except Exception as e:
                logger.warning(f"Error sending trigger {trigger_code} to Biosemi: {e}")
                import traceback
                traceback.print_exc()
        
        # Priority 2: Send to parallel port (if enabled and Biosemi didn't succeed)
        if not success and self.use_triggers and self.parallel_port:
            try:
                self.parallel_port.setData(trigger_code)
                core.wait(hold_duration)  # Hold trigger
                self.parallel_port.setData(0)  # Reset to zero
                success = True
                logger.debug(f"Trigger {trigger_code} sent via parallel port at {timestamp:.3f}s")
            except Exception as e:
                logger.warning(f"Failed to send trigger {trigger_code} via parallel port: {e}")
        
        # Log timestamp AFTER sending trigger (best practice)
        if not success:
            logger.debug(f"Trigger {trigger_code} simulated at {timestamp:.3f}s")
        
        # Priority 3: Always log to CSV mirror file
        self._log_trigger_to_csv(timestamp, trigger_code, event_name, success)
        
        # Store in memory log
        self.trigger_log.append({
            'timestamp': timestamp,
            'trigger_code': trigger_code,
            'event_name': event_name or f'trigger_{trigger_code}',
            'sent_to_eeg': success
        })
        
        return timestamp, success
    
    def _log_trigger_to_csv(self, timestamp: float, trigger_code: int,
                            event_name: Optional[str], sent_to_eeg: bool):
        """Log trigger to CSV file."""
        if self.csv_writer is not None:
            try:
                absolute_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                self.csv_writer.writerow([
                    f'{timestamp:.6f}',
                    absolute_time,
                    trigger_code,
                    event_name or f'trigger_{trigger_code}',
                    'yes' if sent_to_eeg else 'no'
                ])
                # Flush immediately to ensure data is written
                self.csv_file.flush()
            except Exception as e:
                logger.warning(f"Failed to write trigger to CSV: {e}")
    
    def send_trigger_with_logging(self, trigger_code: int, log_stream=None, 
                                   hold_duration: float = 0.01) -> Tuple[float, bool]:
        """
        Send trigger and log to both EEG stream and PsychoPy logging stream.
        
        This is the recommended method for production use.
        Sends trigger to EEG first, then logs to PsychoPy stream.
        
        Parameters
        ----------
        trigger_code : int
            Trigger code to send
        log_stream : optional
            PsychoPy logging stream (if available)
        hold_duration : float
            How long to hold trigger (seconds)
        
        Returns
        -------
        timestamp : float
            Timestamp when trigger was sent
        success : bool
            Whether trigger was sent successfully
        """
        # Send to EEG FIRST (critical)
        timestamp, success = self.send_trigger(trigger_code, hold_duration)
        
        # Then log to PsychoPy stream (if available)
        if log_stream is not None:
            try:
                log_stream.log(f"Trigger {trigger_code} at {timestamp:.3f}s")
            except:
                pass
        
        return timestamp, success
    
    def close(self):
        """Clean up parallel port connection and close CSV file."""
        # Reset parallel port
        if self.parallel_port:
            try:
                self.parallel_port.setData(0)  # Reset to zero
            except:
                pass
            self.parallel_port = None
        
        # Close CSV file
        if self.csv_file is not None:
            try:
                self.csv_file.close()
                logger.info(f"CSV trigger log saved: {self.csv_log_path}")
            except Exception as e:
                logger.warning(f"Error closing CSV file: {e}")
            self.csv_file = None
            self.csv_writer = None
    
    def get_trigger_log(self) -> list:
        """Get in-memory log of all triggers sent."""
        return self.trigger_log.copy()


# Standard trigger codes for semantic visualization paradigm
# OUR experiment's codes (different from reference project)
# Organized with spacing to avoid buffer issues and allow expansion
TRIGGER_CODES = {
    # Trial-level events (base codes)
    'trial_start': 2,
    'fixation': 1,
    
    # Concept presentation (category-specific)
    'concept_category_a': 10,
    'concept_category_b': 20,
    
    # Beep sequence (unique code for each beep to allow detailed analysis)
    'beep_start': 30,
    'beep_1': 31,  # First beep
    'beep_2': 32,  # Second beep
    'beep_3': 33,  # Third beep
    'beep_4': 34,  # Fourth beep
    'beep_5': 35,  # Fifth beep
    'beep_6': 36,  # Sixth beep
    'beep_7': 37,  # Seventh beep
    'beep_8': 38,  # Eighth beep
    
    # Trial completion (base code)
    'trial_end': 40,
    
    # Block-level events (base codes)
    'block_start': 50,
    'block_end': 51
}


def get_trial_start_code(trial_num: int) -> int:
    """
    Get unique trigger code for trial start.
    
    Trial N start = 100 + N
    Range: 101-199 (supports up to 99 trials)
    
    Parameters
    ----------
    trial_num : int
        Trial number (1-indexed)
    
    Returns
    -------
    int
        Trigger code for trial start
    """
    if trial_num < 1 or trial_num > 99:
        raise ValueError(f"Trial number must be between 1 and 99, got {trial_num}")
    return 100 + trial_num


def get_trial_end_code(trial_num: int) -> int:
    """
    Get unique trigger code for trial end.
    
    Trial N end = 200 + N
    Range: 201-299 (supports up to 99 trials)
    
    Parameters
    ----------
    trial_num : int
        Trial number (1-indexed)
    
    Returns
    -------
    int
        Trigger code for trial end
    """
    if trial_num < 1 or trial_num > 99:
        raise ValueError(f"Trial number must be between 1 and 99, got {trial_num}")
    return 200 + trial_num


def get_block_start_code(block_num: int) -> int:
    """
    Get unique trigger code for block start.
    
    Block N start = 150 + N
    Range: 151-159 (supports up to 9 blocks)
    
    Parameters
    ----------
    block_num : int
        Block number (1-indexed)
    
    Returns
    -------
    int
        Trigger code for block start
    """
    if block_num < 1 or block_num > 9:
        raise ValueError(f"Block number must be between 1 and 9, got {block_num}")
    return 150 + block_num


def get_beep_code(beep_num: int, max_beeps: int = 8) -> int:
    """
    Get trigger code for a specific beep number.
    
    Beep N code = 30 + N (where N is 1-indexed)
    Range: 31-38 for beeps 1-8 (supports up to 8 beeps)
    
    Parameters
    ----------
    beep_num : int
        Beep number (1-indexed: 1, 2, 3, ...)
    max_beeps : int
        Maximum number of beeps supported (default: 8)
        
    Returns
    -------
    int
        Trigger code for the beep
    """
    if beep_num < 1 or beep_num > max_beeps:
        raise ValueError(f"Beep number must be between 1 and {max_beeps}, got {beep_num}")
    return 30 + beep_num


def get_beep_codes(n_beeps: int, max_beeps: int = 8) -> List[int]:
    """
    Get list of trigger codes for N beeps.
    
    Parameters
    ----------
    n_beeps : int
        Number of beeps needed
    max_beeps : int
        Maximum number of beeps supported (default: 8)
        
    Returns
    -------
    list
        List of trigger codes for beeps 1 through n_beeps
    """
    if n_beeps < 1 or n_beeps > max_beeps:
        raise ValueError(f"Number of beeps must be between 1 and {max_beeps}, got {n_beeps}")
    return [get_beep_code(i, max_beeps) for i in range(1, n_beeps + 1)]


def get_block_end_code(block_num: int) -> int:
    """
    Get unique trigger code for block end.
    
    Block N end = 250 + N
    Range: 251-259 (supports up to 9 blocks)
    
    Parameters
    ----------
    block_num : int
        Block number (1-indexed)
    
    Returns
    -------
    int
        Trigger code for block end
    """
    if block_num < 1 or block_num > 9:
        raise ValueError(f"Block number must be between 1 and 9, got {block_num}")
    return 250 + block_num


def create_trigger_handler(port_address: int = 0x0378, use_triggers: bool = False,
                           csv_log_path: Optional[Path] = None,
                           biosemi_connection: Optional['serial.Serial'] = None) -> TriggerHandler:
    """
    Factory function to create trigger handler.
    
    Parameters
    ----------
    port_address : int
        Parallel port address
    use_triggers : bool
        Whether to enable triggers
    csv_log_path : Path, optional
        Path to CSV file for trigger logging (mirror log)
    biosemi_connection : serial.Serial, optional
        Biosemi serial port connection. If provided, triggers will be sent to Biosemi.
    
    Returns
    -------
    TriggerHandler
        Initialized trigger handler
    """
    return TriggerHandler(
        port_address=port_address,
        use_triggers=use_triggers,
        csv_log_path=csv_log_path,
        biosemi_connection=biosemi_connection
    )
