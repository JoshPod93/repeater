"""
Display utilities for visual stimulus presentation.

Handles creation and management of visual stimuli for the semantic visualization paradigm.
"""

from psychopy import visual
from typing import Optional, Tuple


def create_window(size: Tuple[int, int] = (1024, 768), 
                  color: str = 'black',
                  fullscreen: bool = False,
                  units: str = 'height') -> visual.Window:
    """
    Create PsychoPy window for experiment.
    
    Parameters
    ----------
    size : tuple
        Window size (width, height)
    color : str
        Background color
    fullscreen : bool
        Whether to use fullscreen mode
    units : str
        Coordinate units ('height', 'pix', etc.)
    
    Returns
    -------
    visual.Window
        PsychoPy window object
    """
    return visual.Window(
        size=size,
        color=color,
        units=units,
        fullscr=fullscreen
    )


def create_fixation_cross(win: visual.Window,
                          height: float = 0.1,
                          color: str = 'white') -> visual.TextStim:
    """
    Create fixation cross stimulus.
    
    Parameters
    ----------
    win : visual.Window
        Window to draw on
    height : float
        Height of fixation cross
    color : str
        Color of fixation cross
    
    Returns
    -------
    visual.TextStim
        Fixation cross stimulus
    """
    return visual.TextStim(
        win,
        text='+',
        height=height,
        color=color
    )


def create_text_stimulus(win: visual.Window,
                         text: str = '',
                         height: float = 0.08,
                         color: str = 'white',
                         bold: bool = True,
                         pos: Optional[Tuple[float, float]] = None) -> visual.TextStim:
    """
    Create text stimulus for concept presentation.
    
    Parameters
    ----------
    win : visual.Window
        Window to draw on
    text : str
        Text to display
    height : float
        Text height
    color : str
        Text color
    bold : bool
        Whether text is bold
    pos : tuple, optional
        Position (x, y)
    
    Returns
    -------
    visual.TextStim
        Text stimulus
    """
    stim = visual.TextStim(
        win,
        text=text,
        height=height,
        color=color,
        bold=bold
    )
    
    if pos is not None:
        stim.pos = pos
    
    return stim


def create_instruction_text(win: visual.Window,
                           instruction_text: str,
                           height: float = 0.04,
                           color: str = 'white',
                           wrap_width: float = 0.8) -> visual.TextStim:
    """
    Create instruction text stimulus.
    
    Parameters
    ----------
    win : visual.Window
        Window to draw on
    instruction_text : str
        Instruction text to display
    height : float
        Text height
    color : str
        Text color
    wrap_width : float
        Width for text wrapping
    
    Returns
    -------
    visual.TextStim
        Instruction text stimulus
    """
    return visual.TextStim(
        win,
        text=instruction_text,
        height=height,
        color=color,
        wrapWidth=wrap_width
    )


def create_progress_indicator(win: visual.Window,
                              height: float = 0.03,
                              color: str = 'gray',
                              pos: Tuple[float, float] = (0, -0.4)) -> visual.TextStim:
    """
    Create progress indicator text.
    
    Parameters
    ----------
    win : visual.Window
        Window to draw on
    height : float
        Text height
    color : str
        Text color
    pos : tuple
        Position (x, y)
    
    Returns
    -------
    visual.TextStim
        Progress indicator stimulus
    """
    return visual.TextStim(
        win,
        text='',
        height=height,
        color=color,
        pos=pos
    )


def create_visual_mask(win: visual.Window,
                       height: float = 0.08,
                       color: str = 'white') -> visual.TextStim:
    """
    Create simple text-based visual mask for orthographic stimuli.
    
    Uses a pattern of hash symbols to mask text stimuli - standard practice
    for orthographic masking to prevent afterimages.
    
    Parameters
    ----------
    win : visual.Window
        Window to draw on
    height : float
        Text height (should match concept text height)
    color : str
        Text color
    
    Returns
    -------
    visual.TextStim
        Visual mask stimulus (hash pattern)
    """
    # Simple hash pattern mask - standard for orthographic stimuli
    mask_text = '####'
    return visual.TextStim(
        win,
        text=mask_text,
        height=height,
        color=color,
        bold=True
    )


class DisplayManager:
    """
    Manager for all visual stimuli in the experiment.
    
    Centralizes creation and management of visual elements.
    """
    
    def __init__(self, win: visual.Window, config: dict):
        """
        Initialize display manager.
        
        Parameters
        ----------
        win : visual.Window
            PsychoPy window
        config : dict
            Configuration dictionary with display parameters
        """
        self.win = win
        self.config = config
        
        # Create all stimuli
        self.fixation = create_fixation_cross(
            win,
            height=config.get('fixation_height', 0.1),
            color=config.get('text_color', 'white')
        )
        
        self.concept_text = create_text_stimulus(
            win,
            height=config.get('text_height', 0.08),
            color=config.get('text_color', 'white'),
            bold=config.get('bold_text', True)
        )
        
        self.instruction_text = create_instruction_text(
            win,
            instruction_text=config.get('instruction_text', ''),
            height=0.04,
            color=config.get('text_color', 'white')
        )
        
        self.progress_text = create_progress_indicator(
            win,
            height=0.03,
            color='gray'
        )
        
        self.visual_mask = create_visual_mask(
            win,
            height=config.get('text_height', 0.08),
            color=config.get('text_color', 'white')
        )
    
    def show_fixation(self):
        """Display fixation cross."""
        self.fixation.draw()
        self.win.flip()
    
    def show_concept(self, concept: str, case: str = 'lower'):
        """
        Display concept word.
        
        Parameters
        ----------
        concept : str
            Concept to display
        case : str
            Case to display: 'upper' for uppercase, 'lower' for lowercase (default: 'lower')
        """
        # Apply case transformation
        if case == 'upper':
            display_text = concept.upper()
        else:
            display_text = concept.lower()
        
        self.concept_text.text = display_text
        self.concept_text.draw()
        self.win.flip()
    
    def show_trial_indicator(self, trial_num: int, total_trials: int):
        """
        Display trial indicator as centered text (like concept word).
        
        Parameters
        ----------
        trial_num : int
            Current trial number
        total_trials : int
            Total number of trials
        """
        indicator_text = f"Trial {trial_num}/{total_trials}"
        # Use concept_text stimulus to display trial indicator (centered, same style)
        self.concept_text.text = indicator_text
        self.concept_text.draw()
        self.win.flip()
    
    def show_instructions(self):
        """Display instruction screen."""
        self.instruction_text.draw()
        self.win.flip()
    
    def show_mask(self):
        """
        Display visual mask (text-based hash pattern to prevent afterimages).
        
        Shows a simple hash pattern mask to erase any afterimages from concept presentation.
        Standard practice for orthographic (text) stimuli masking.
        """
        self.visual_mask.draw()
        self.win.flip()
    
    
    def clear_screen(self):
        """Clear screen (blank display)."""
        self.win.flip()
    
    def show_text(self, text: str, height: float = 0.05, color: str = 'white'):
        """
        Display arbitrary text.
        
        Clears any previous content and shows new text.
        
        Parameters
        ----------
        text : str
            Text to display
        height : float
            Text height
        color : str
            Text color
        """
        # Clear screen first by flipping to blank
        self.win.flip()
        
        # Create and show text
        temp_text = create_text_stimulus(
            self.win,
            text=text,
            height=height,
            color=color
        )
        temp_text.draw()
        self.win.flip()
