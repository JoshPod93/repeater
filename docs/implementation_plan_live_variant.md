# Implementation Plan: Live Biosemi Variant

## Overview

This plan outlines the steps to:
1. **Remove** the old non-sim variant (`paradigm/semantic_paradigm.py`)
2. **Create** a new live variant (`paradigm/semantic_paradigm_live.py`) based on the fully-debugged simulation variant
3. **Integrate** Biosemi live data capture based on patterns from `grasp/paradigm`

## Current State Analysis

### Simulation Variant (KEEP & USE AS BASE)
- **File:** `paradigm/semantic_paradigm_simulation.py`
- **Status:** ✅ Fully functional, debugged, and validated
- **Features:**
  - Block-based data organization with auto-detection
  - Stratified randomization protocol generation
  - CSV trigger mirror logging
  - Dynamic beep count support
  - All trigger codes properly implemented
  - Complete trial/block management

### Old Non-Sim Variant (REMOVE)
- **File:** `paradigm/semantic_paradigm.py`
- **Status:** ❌ Outdated, class-based, missing features
- **Issues:**
  - Doesn't have block management
  - Missing stratified randomization
  - No auto-detection of next block
  - Different structure from sim variant

### Reference Implementation
- **Location:** `c:\Users\jp24194\Box\Semantic BCI Project\grasp\paradigm`
- **Key Patterns:**
  - Serial port communication (pyserial) for Biosemi triggers
  - Global serial port instance opened at experiment start
  - Immediate flush() after each trigger
  - 5ms delay between triggers
  - CSV mirror logging for verification

## Implementation Steps

### Phase 1: Create Biosemi Utilities

#### Step 1.1: Create `paradigm/utils/biosemi_utils.py`
**Purpose:** Biosemi connection and trigger management

**Key Functions:**
```python
# Global serial port instance (similar to grasp/paradigm pattern)
_serial_port = None

def connect_biosemi(port: str = 'COM3', baudrate: int = 115200) -> serial.Serial:
    """
    Open serial port connection to Biosemi hardware.
    
    Returns serial.Serial object or raises exception.
    - Opens port with 8N1 configuration
    - Clears input/output buffers
    - Flushes to ensure clean state
    """
    pass

def verify_biosemi_connection(connection: serial.Serial) -> bool:
    """
    Verify Biosemi connection is active and ready.
    
    Returns True if connection is valid, False otherwise.
    """
    pass

def send_biosemi_trigger(connection: serial.Serial, trigger_code: int) -> bool:
    """
    Send trigger byte to Biosemi via serial port.
    
    Critical steps:
    1. Write trigger byte
    2. Flush immediately (prevents buffering)
    3. Wait 5ms (prevents rapid-fire errors)
    
    Returns True if successful, False otherwise.
    """
    pass

def close_biosemi_connection(connection: serial.Serial):
    """
    Cleanly close Biosemi connection.
    - Reset output buffer
    - Close port
    - Clear global instance
    """
    pass
```

**Reference:** Adapt from `grasp/paradigm/paradigm_utils.py`:
- `open_serial_port()` function
- `_send_eeg_trigger()` function
- `close_serial_port()` function

---

### Phase 2: Update Trigger Handler

#### Step 2.1: Modify `paradigm/utils/trigger_utils.py`
**Changes:**
1. Add `biosemi_connection` parameter to `TriggerHandler.__init__()`
2. Update `send_trigger()` to support Biosemi:
   - Priority: Biosemi > Parallel Port > Simulation
   - Send to Biosemi FIRST (if connected)
   - Then send to parallel port (if enabled)
   - Always log to CSV

**Modified Signature:**
```python
class TriggerHandler:
    def __init__(self, 
                 port_address: int = 0x0378, 
                 use_triggers: bool = False,
                 csv_log_path: Optional[Path] = None,
                 biosemi_connection: Optional[serial.Serial] = None):  # NEW
        """
        biosemi_connection: If provided, triggers will be sent to Biosemi
        """
        self.biosemi_connection = biosemi_connection
        # ... existing code ...

    def send_trigger(self, trigger_code: int, ...):
        """
        Updated priority:
        1. Send to Biosemi data stream (if connected)
        2. Send to parallel port (if enabled)
        3. Log to CSV (always)
        """
        # Send to Biosemi FIRST
        if self.biosemi_connection and self.biosemi_connection.is_open:
            from paradigm.utils.biosemi_utils import send_biosemi_trigger
            send_biosemi_trigger(self.biosemi_connection, trigger_code)
        
        # Then send to parallel port (existing code)
        if self.use_triggers and self.parallel_port:
            # ... existing parallel port code ...
        
        # Always log to CSV
        # ... existing CSV logging ...
```

**Update Factory Function:**
```python
def create_trigger_handler(port_address: int = 0x0378, 
                           use_triggers: bool = False,
                           csv_log_path: Optional[Path] = None,
                           biosemi_connection: Optional[serial.Serial] = None) -> TriggerHandler:
    """Factory function with Biosemi support."""
    return TriggerHandler(
        port_address=port_address,
        use_triggers=use_triggers,
        csv_log_path=csv_log_path,
        biosemi_connection=biosemi_connection
    )
```

---

### Phase 3: Create Live Experiment Variant

#### Step 3.1: Create `paradigm/semantic_paradigm_live.py`
**Base:** Copy `paradigm/semantic_paradigm_simulation.py` and modify

**Key Changes:**

1. **Import Biosemi utilities:**
```python
from paradigm.utils.biosemi_utils import (
    connect_biosemi, verify_biosemi_connection, 
    close_biosemi_connection
)
```

2. **Update `run_experiment_live()` function:**
   - Add `biosemi_port` parameter (default: 'COM3' or from config)
   - Connect to Biosemi at start
   - Verify connection before proceeding
   - Pass Biosemi connection to trigger handler
   - Use `use_triggers=True` (real triggers)
   - Use fullscreen mode (not windowed)
   - Save to `data/results/` (not `sim_data/sim_results/`)
   - Clean up Biosemi connection on exit

3. **Modify trial function:**
   - Rename `run_single_trial_simulation()` → `run_single_trial_live()`
   - Remove `[SIM]` prefixes from print statements
   - Keep all timing and trigger logic identical

4. **Update visualization period:**
   - Keep `simulate_visualization_period()` function name (it's just a name)
   - OR rename to `run_visualization_period()` for clarity
   - Functionality stays the same (beeps with fixation)

5. **Error handling:**
   - Try/except around Biosemi connection
   - Graceful fallback with warning if connection fails
   - Always clean up on exit (finally block)

**Structure:**
```python
def run_experiment_live(
    participant_id: str,
    biosemi_port: str = 'COM3',  # Serial port (not parallel port address)
    config_path: Optional[Path] = None,
    n_trials: Optional[int] = None,
    n_beeps: Optional[int] = None,
    verbose: bool = True
) -> Dict[str, any]:
    """
    Run experiment with live Biosemi EEG data capture.
    
    Steps:
    1. Connect to Biosemi hardware
    2. Verify connection
    3. Initialize trigger handler with Biosemi connection
    4. Run experiment (same structure as simulation)
    5. Clean up Biosemi connection
    """
    # Connect to Biosemi
    biosemi_conn = None
    try:
        biosemi_conn = connect_biosemi(port=biosemi_port)
        if not verify_biosemi_connection(biosemi_conn):
            raise RuntimeError("Biosemi connection verification failed")
        print(f"[BIOSEMI] Connected to {biosemi_port}")
    except Exception as e:
        print(f"[WARNING] Biosemi connection failed: {e}")
        print("[WARNING] Continuing without Biosemi (triggers will be simulated)")
        # Continue anyway (for testing)
    
    # Initialize trigger handler with Biosemi
    trigger_handler = create_trigger_handler(
        port_address=config.get('PARALLEL_PORT_ADDRESS', 0x0378),
        use_triggers=True,  # Real triggers
        biosemi_connection=biosemi_conn,  # NEW
        csv_log_path=csv_log_path
    )
    
    # Create window (FULLSCREEN for live experiments)
    win = create_window(
        size=config.get('WINDOW_SIZE', (1024, 768)),
        color=config.get('BACKGROUND_COLOR', 'black'),
        fullscreen=True  # Fullscreen for live experiments
    )
    
    # ... rest of experiment code (same as simulation) ...
    
    finally:
        # Always clean up Biosemi connection
        if biosemi_conn:
            close_biosemi_connection(biosemi_conn)
            print("[BIOSEMI] Connection closed")
```

**Data Organization:**
- Save to `data/results/` (not `sim_data/sim_results/`)
- Same folder structure as simulation:
  - `data/results/sub-{participant_id}_{timestamp}/`
  - `Block_{N:04d}/` folders
  - CSV trigger logs in subject folder

---

### Phase 4: Remove Old Variant

#### Step 4.1: Delete `paradigm/semantic_paradigm.py`
**Reason:** Outdated, missing features, different structure

**Before deleting:**
- Check if any scripts import from it
- Update any references to point to live variant
- Document removal in commit message

#### Step 4.2: Update any launch scripts
- Check `paradigm/scripts/run_experiment.py`
- Update to use `semantic_paradigm_live.py` instead

---

### Phase 5: Update Configuration

#### Step 5.1: Add Biosemi config to `config/experiment_config.py`
```python
# Biosemi Configuration
BIOSEMI_PORT = 'COM3'  # Serial port for Biosemi (Windows)
BIOSEMI_BAUDRATE = 115200  # Serial port baudrate
BIOSEMI_ENABLED = True  # Enable Biosemi connection
```

---

### Phase 6: Update Launch Scripts

#### Step 6.1: Modify `paradigm/scripts/run_experiment.py`
**Add:**
- `--live` flag to enable Biosemi mode
- `--biosemi-port` option for port configuration
- Connection verification before experiment starts

**Example:**
```python
parser.add_argument('--live', action='store_true',
                   help='Run with live Biosemi EEG capture')
parser.add_argument('--biosemi-port', type=str, default='COM3',
                   help='Serial port for Biosemi (default: COM3)')
```

---

### Phase 7: Testing Scripts

#### Step 7.1: Create `scripts/test_biosemi_connection.py`
**Purpose:** Test Biosemi connection without running experiment

```python
def test_connection(port: str = 'COM3'):
    """Test Biosemi connection."""
    try:
        conn = connect_biosemi(port=port)
        if verify_biosemi_connection(conn):
            print(f"[OK] Biosemi connected to {port}")
            close_biosemi_connection(conn)
            return True
        else:
            print(f"[FAIL] Biosemi connection verification failed")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
```

#### Step 7.2: Create `scripts/test_biosemi_triggers.py`
**Purpose:** Send test triggers to Biosemi

```python
def test_triggers(port: str = 'COM3', n_triggers: int = 10):
    """Send test triggers to Biosemi."""
    conn = connect_biosemi(port=port)
    for i in range(n_triggers):
        send_biosemi_trigger(conn, i + 1)
        print(f"Sent trigger {i + 1}")
        time.sleep(0.1)
    close_biosemi_connection(conn)
```

---

### Phase 8: Documentation Updates

#### Step 8.1: Update `README.md`
- Add live experiment instructions
- Document Biosemi setup requirements
- Add troubleshooting section

#### Step 8.2: Create `docs/biosemi_setup.md`
- Hardware setup instructions
- Port configuration
- Connection troubleshooting
- Trigger verification procedures

---

## File Changes Summary

### New Files:
1. `paradigm/utils/biosemi_utils.py` - Biosemi connection utilities
2. `paradigm/semantic_paradigm_live.py` - Live experiment variant
3. `scripts/test_biosemi_connection.py` - Connection testing
4. `scripts/test_biosemi_triggers.py` - Trigger testing
5. `docs/biosemi_setup.md` - Setup documentation

### Modified Files:
1. `paradigm/utils/trigger_utils.py` - Add Biosemi support
2. `paradigm/scripts/run_experiment.py` - Add live mode flags
3. `config/experiment_config.py` - Add Biosemi configuration
4. `README.md` - Update with live experiment instructions

### Deleted Files:
1. `paradigm/semantic_paradigm.py` - Old non-sim variant (outdated)

---

## Testing Checklist

### Pre-Integration:
- [ ] Biosemi connection utility works
- [ ] Trigger handler sends to Biosemi correctly
- [ ] Error handling works for connection failures
- [ ] Cleanup functions properly close connections

### Integration:
- [ ] Short experiment (1 trial) captures data correctly
- [ ] Triggers appear in CSV mirror log
- [ ] Timing synchronization is accurate
- [ ] Block management works correctly

### Full Testing:
- [ ] Complete block runs without errors
- [ ] Multiple blocks work correctly
- [ ] Data files are saved properly
- [ ] All triggers match protocol

---

## Dependencies

### New Dependencies:
- `pyserial` - For serial port communication with Biosemi

**Add to `requirements.txt`:**
```
pyserial>=3.5
```

---

## Implementation Order

1. **Phase 1:** Create Biosemi utilities (foundation)
2. **Phase 2:** Update trigger handler (integration point)
3. **Phase 3:** Create live variant (main work)
4. **Phase 4:** Remove old variant (cleanup)
5. **Phase 5:** Update configuration (configuration)
6. **Phase 6:** Update launch scripts (usability)
7. **Phase 7:** Create testing scripts (validation)
8. **Phase 8:** Update documentation (completion)

---

## Success Criteria

1. ✅ Biosemi connection established at experiment start
2. ✅ Triggers sent to Biosemi data stream successfully
3. ✅ CSV mirror logs match all trigger codes
4. ✅ Error handling works for all failure scenarios
5. ✅ Data organization matches simulation structure
6. ✅ Cleanup functions properly on exit
7. ✅ Old variant removed, no broken references
8. ✅ Documentation updated with live experiment instructions

---

## Notes

- **Self-Sufficiency:** Do not import from `grasp/paradigm` directly. Copy/adapt code as needed.
- **Backward Compatibility:** Simulation mode must continue to work unchanged.
- **Trigger Protocols:** Follow established patterns from `grasp/paradigm` for Biosemi trigger sending.
- **Data Organization:** Live experiments use `data/results/` (not `sim_data/sim_results/`).
- **Validation:** All triggers must be validated against protocol, same as simulation.
