"""
Audio utilities for creating beep sounds.

Handles PsychoPy sound creation with compatibility fallbacks.
"""

from psychopy import sound
from typing import Optional
import warnings


def create_beep_sound(frequency: int = 440, duration: float = 0.1, 
                     fallback_note: str = 'A', octave: int = 4) -> Optional[sound.Sound]:
    """
    Create beep sound with multiple fallback strategies.
    
    Tries different methods to create sound based on PsychoPy version compatibility.
    
    Parameters
    ----------
    frequency : int
        Frequency in Hz (default: 440)
    duration : float
        Duration in seconds (default: 0.1)
    fallback_note : str
        Fallback note name if frequency fails
    octave : int
        Octave for note-based sound
    
    Returns
    -------
    sound.Sound or None
        Sound object or None if all methods fail
    """
    # Try method 1: Frequency-based sound
    try:
        beep = sound.Sound(value=frequency, secs=duration)
        return beep
    except Exception as e1:
        warnings.warn(f"Frequency-based sound failed: {e1}")
        
        # Try method 2: Note-based sound
        try:
            beep = sound.Sound(fallback_note, octave=octave, secs=duration)
            return beep
        except Exception as e2:
            warnings.warn(f"Note-based sound failed: {e2}")
            
            # Try method 3: Simple tone using value parameter
            try:
                beep = sound.Sound(value='C', secs=duration)
                return beep
            except Exception as e3:
                warnings.warn(f"All sound creation methods failed: {e1}, {e2}, {e3}")
                return None


def play_beep(beep_sound: Optional[sound.Sound], stop_first: bool = True):
    """
    Play beep sound with error handling.
    
    Parameters
    ----------
    beep_sound : sound.Sound or None
        Sound object to play
    stop_first : bool
        Whether to stop sound before playing (ensures clean playback)
    """
    if beep_sound is None:
        return
    
    try:
        if stop_first:
            beep_sound.stop()
        beep_sound.play()
    except Exception as e:
        warnings.warn(f"Failed to play beep: {e}")
