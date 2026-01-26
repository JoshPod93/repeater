"""
Trigger utilities for EEG synchronization.

Handles parallel port communication for sending trigger codes to EEG systems.
Based on best practices: send trigger to EEG stream first, then log to PsychoPy.
"""

from psychopy import parallel, core
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TriggerHandler:
    """
    Handler for EEG trigger communication via parallel port.
    
    Follows best practice: send trigger to EEG stream first, then log.
    """
    
    def __init__(self, port_address: int = 0x0378, use_triggers: bool = False):
        """
        Initialize trigger handler.
        
        Parameters
        ----------
        port_address : int
            Parallel port address (default 0x0378 for LPT1)
        use_triggers : bool
            Whether to actually send triggers (False for testing)
        """
        self.port_address = port_address
        self.use_triggers = use_triggers
        self.parallel_port = None
        self.clock = core.Clock()
        
        if self.use_triggers:
            try:
                self.parallel_port = parallel.ParallelPort(address=port_address)
                logger.info(f"Parallel port initialized at {hex(port_address)}")
            except Exception as e:
                logger.warning(f"Could not initialize parallel port: {e}. Triggers disabled.")
                self.use_triggers = False
                self.parallel_port = None
    
    def send_trigger(self, trigger_code: int, hold_duration: float = 0.01) -> Tuple[float, bool]:
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
        
        return timestamp, success
    
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
        """Clean up parallel port connection."""
        if self.parallel_port:
            try:
                self.parallel_port.setData(0)  # Reset to zero
            except:
                pass
            self.parallel_port = None


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


def create_trigger_handler(port_address: int = 0x0378, use_triggers: bool = False) -> TriggerHandler:
    """
    Factory function to create trigger handler.
    
    Parameters
    ----------
    port_address : int
        Parallel port address
    use_triggers : bool
        Whether to enable triggers
    
    Returns
    -------
    TriggerHandler
        Initialized trigger handler
    """
    return TriggerHandler(port_address=port_address, use_triggers=use_triggers)
