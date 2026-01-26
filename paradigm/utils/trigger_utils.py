"""
Trigger utilities for EEG synchronization.

Handles parallel port communication for sending trigger codes to EEG systems.
Based on best practices: send trigger to EEG stream first, then log to PsychoPy.
Includes CSV mirror logging for trigger verification.
"""

from psychopy import parallel, core
from typing import Optional, Tuple
from pathlib import Path
import csv
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TriggerHandler:
    """
    Handler for EEG trigger communication via parallel port.
    
    Follows best practice: send trigger to EEG stream first, then log.
    Includes CSV mirror logging for trigger verification.
    """
    
    def __init__(self, port_address: int = 0x0378, use_triggers: bool = False,
                 csv_log_path: Optional[Path] = None):
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
        """
        self.port_address = port_address
        self.use_triggers = use_triggers
        self.parallel_port = None
        self.clock = core.Clock()
        self.csv_log_path = csv_log_path
        self.csv_file = None
        self.csv_writer = None
        self.trigger_log = []  # In-memory log of all triggers
        
        # Initialize CSV logging if path provided
        if self.csv_log_path is not None:
            self._init_csv_logging()
        
        if self.use_triggers:
            try:
                self.parallel_port = parallel.ParallelPort(address=port_address)
                logger.info(f"Parallel port initialized at {hex(port_address)}")
            except Exception as e:
                logger.warning(f"Could not initialize parallel port: {e}. Triggers disabled.")
                self.use_triggers = False
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
        
        Parameters
        ----------
        trigger_code : int
            Trigger code to send (0-255)
        hold_duration : float
            How long to hold trigger high (seconds, default 0.01)
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
        
        # Send trigger to EEG stream FIRST (critical for synchronization)
        if self.use_triggers and self.parallel_port:
            try:
                self.parallel_port.setData(trigger_code)
                core.wait(hold_duration)  # Hold trigger
                self.parallel_port.setData(0)  # Reset to zero
                success = True
            except Exception as e:
                logger.warning(f"Failed to send trigger {trigger_code}: {e}")
        
        # Log timestamp AFTER sending trigger (best practice)
        if success:
            logger.debug(f"Trigger {trigger_code} sent at {timestamp:.3f}s")
        else:
            logger.debug(f"Trigger {trigger_code} simulated at {timestamp:.3f}s")
        
        # Log to CSV mirror file
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
TRIGGER_CODES = {
    'fixation': 1,
    'concept_category_a': 10,
    'concept_category_b': 20,
    'beep_start': 30,
    'beep': 31,
    'trial_end': 40,
    'block_start': 50,
    'block_end': 51
}


def create_trigger_handler(port_address: int = 0x0378, use_triggers: bool = False,
                           csv_log_path: Optional[Path] = None) -> TriggerHandler:
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
    
    Returns
    -------
    TriggerHandler
        Initialized trigger handler
    """
    return TriggerHandler(port_address=port_address, use_triggers=use_triggers,
                         csv_log_path=csv_log_path)
