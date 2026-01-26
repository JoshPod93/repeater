"""
Paradigm utilities package.

Provides utilities for trigger handling, display management, data logging, and randomization.
"""

from .trigger_utils import (
    TriggerHandler,
    TRIGGER_CODES,
    create_trigger_handler
)

from .display_utils import (
    create_window,
    create_fixation_cross,
    create_text_stimulus,
    create_instruction_text,
    create_progress_indicator,
    DisplayManager
)

from .data_utils import (
    create_metadata,
    create_trial_data_dict,
    save_trial_data,
    load_trial_data,
    print_experiment_summary
)

from .randomization_utils import (
    create_balanced_sequence,
    create_date_seeded_sequence,
    validate_trial_sequence,
    shuffle_trials
)

__all__ = [
    # Trigger utilities
    'TriggerHandler',
    'TRIGGER_CODES',
    'create_trigger_handler',
    # Display utilities
    'create_window',
    'create_fixation_cross',
    'create_text_stimulus',
    'create_instruction_text',
    'create_progress_indicator',
    'DisplayManager',
    # Data utilities
    'create_metadata',
    'create_trial_data_dict',
    'save_trial_data',
    'load_trial_data',
    'print_experiment_summary',
    # Randomization utilities
    'create_balanced_sequence',
    'create_date_seeded_sequence',
    'validate_trial_sequence',
    'shuffle_trials'
]
