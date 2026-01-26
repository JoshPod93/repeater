"""
Timing utilities with intelligent jittering for experimental paradigms.

Provides jittered timing functions to prevent temporal predictability
and reduce anticipatory responses in participants.
"""

import random
from typing import Optional


def jittered_wait(base_duration: float, jitter_range: float = 0.1) -> float:
    """
    Generate jittered wait duration.
    
    Jitters timing by ±jitter_range percentage of base duration.
    Default is ±10% (0.1), so 1.0s becomes 0.9-1.1s.
    
    Parameters
    ----------
    base_duration : float
        Base duration in seconds
    jitter_range : float
        Jitter range as fraction (default 0.1 = ±10%)
    
    Returns
    -------
    float
        Jittered duration in seconds
    """
    jitter_amount = base_duration * jitter_range
    min_duration = base_duration - jitter_amount
    max_duration = base_duration + jitter_amount
    
    return random.uniform(min_duration, max_duration)


def get_jittered_duration(base_duration: float, jitter_range: float = 0.1) -> float:
    """
    Get jittered duration value (alias for jittered_wait for clarity).
    
    Parameters
    ----------
    base_duration : float
        Base duration in seconds
    jitter_range : float
        Jitter range as fraction (default 0.1 = ±10%)
    
    Returns
    -------
    float
        Jittered duration in seconds
    """
    return jittered_wait(base_duration, jitter_range)
