# Next Steps: Biosemi Live EEG Integration

## Overview

This document outlines the steps required to integrate the semantic visualization paradigm with live Biosemi EEG data capture. The simulation variant (`semantic_paradigm_simulation.py`) is fully functional and validated. The next phase involves creating a "live" variant that connects to Biosemi hardware, sends triggers to the data stream, and enables real-time data capture during experiments.

## Current Status

### ✅ Completed
- **Simulation variant** (`paradigm/semantic_paradigm_simulation.py`) fully functional
- **Trigger system** implemented with parallel port support (`paradigm/utils/trigger_utils.py`)
- **Trigger validation** script working correctly (`scripts/validate_triggers.py`)
- **Block-based data organization** with subject folders
- **CSV mirror logging** for trigger verification
- **Stratified randomization** protocol generation
- **All stimulus features** tested and validated

### 🔄 Next Phase: Live Biosemi Integration

## Reference: grasp/paradigm Project Structure

The `grasp/paradigm` project (located at `c:\Users\jp24194\Box\Semantic BCI Project\grasp\paradigm`) provides the reference implementation for Biosemi integration. Key components to reference:

1. **Biosemi connection/launch** - How to initialize and connect to Biosemi hardware
2. **Trigger protocols** - Established methods for sending triggers to Biosemi data stream
3. **Data stream synchronization** - Ensuring triggers are properly embedded in BDF files
4. **Error handling** - Managing connection failures and recovery

**Note:** The codebase should be self-sufficient. Copy/adapt functionality from `grasp/paradigm` as needed rather than importing directly.

## Implementation Steps

### Step 1: Create Biosemi Connection Utility

**File:** `paradigm/utils/biosemi_utils.py` (new file)

**Requirements:**
- Initialize Biosemi connection at experiment start
- Handle connection errors gracefully
- Provide connection status checking
- Follow patterns from `grasp/paradigm` project

**Key Functions Needed:**
```python
def connect_biosemi(port_address: int = 0x0378) -> BiosemiConnection:
    """
    Connect to Biosemi hardware and initialize data stream.
    
    Returns BiosemiConnection object or raises exception.
    """
    pass

def verify_biosemi_connection(connection: BiosemiConnection) -> bool:
    """
    Verify Biosemi connection is active and ready.
    
    Returns True if connection is valid, False otherwise.
    """
    pass

def close_biosemi_connection(connection: BiosemiConnection):
    """
    Cleanly close Biosemi connection and data stream.
    """
    pass
```

**Reference:** Check `grasp/paradigm` for Biosemi initialization patterns.

### Step 2: Update Trigger Handler for Biosemi

**File:** `paradigm/utils/trigger_utils.py` (modify existing)

**Changes Needed:**
- Add Biosemi-specific trigger sending method
- Ensure triggers are sent to Biosemi data stream (not just parallel port)
- Maintain backward compatibility with simulation mode
- Follow established trigger protocols from `grasp/paradigm`

**Key Modifications:**
```python
class TriggerHandler:
    def __init__(self, ..., biosemi_connection: Optional[BiosemiConnection] = None):
        """
        Add biosemi_connection parameter.
        If provided, send triggers to Biosemi data stream.
        """
        self.biosemi_connection = biosemi_connection
        # ... existing code ...
    
    def send_trigger(self, trigger_code: int, ...):
        """
        Update to send triggers to Biosemi if connection exists.
        Priority: Biosemi > Parallel Port > Simulation
        """
        # 1. Send to Biosemi data stream FIRST (if connected)
        # 2. Send to parallel port (if enabled)
        # 3. Log to CSV (always)
        pass
```

**Reference:** Check `grasp/paradigm/trigger_utils.py` for Biosemi trigger patterns.

### Step 3: Create Live Experiment Variant

**File:** `paradigm/semantic_paradigm_live.py` (new file)

**Based on:** `paradigm/semantic_paradigm_simulation.py`

**Key Differences:**
- Connect to Biosemi at experiment start
- Use real triggers (not simulated)
- Handle Biosemi connection errors
- Provide connection status feedback
- Ensure proper cleanup on exit

**Structure:**
```python
def run_experiment_live(
    participant_id: str,
    biosemi_port: int = 0x0378,
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
    4. Run experiment (same as simulation, but with real triggers)
    5. Clean up Biosemi connection
    """
    # Connect to Biosemi
    biosemi_conn = connect_biosemi(port_address=biosemi_port)
    
    # Verify connection
    if not verify_biosemi_connection(biosemi_conn):
        raise RuntimeError("Biosemi connection failed")
    
    # Initialize trigger handler with Biosemi
    trigger_handler = create_trigger_handler(
        port_address=biosemi_port,
        use_triggers=True,
        biosemi_connection=biosemi_conn,  # NEW
        csv_log_path=csv_log_path
    )
    
    # Run experiment (reuse simulation logic)
    # ... rest of experiment code ...
    
    # Clean up
    close_biosemi_connection(biosemi_conn)
```

### Step 4: Update Launch Script

**File:** `paradigm/scripts/run_experiment.py` (modify existing)

**Add:**
- `--live` flag to enable Biosemi mode
- `--biosemi-port` option for port configuration
- Connection verification before experiment starts
- Error handling for connection failures

**Example:**
```bash
# Live experiment with Biosemi
python paradigm/semantic_paradigm_live.py --participant-id P001 --live --biosemi-port 0x0378

# Or use existing launcher with flags
python paradigm/scripts/run_experiment.py --participant-id P001 --live
```

### Step 5: Testing with Live Data Capture

**Test Sequence:**

1. **Connection Test:**
   ```bash
   # Test Biosemi connection only (no experiment)
   python scripts/test_biosemi_connection.py --port 0x0378
   ```

2. **Trigger Test:**
   ```bash
   # Send test triggers to Biosemi
   python scripts/test_biosemi_triggers.py --port 0x0378 --n-triggers 10
   ```

3. **Short Experiment Test:**
   ```bash
   # Run minimal experiment (1 trial, 3 beeps)
   python paradigm/semantic_paradigm_live.py \
       --participant-id test_001 \
       --live \
       --n-trials 1 \
       --n-beeps 3
   ```

4. **Full Block Test:**
   ```bash
   # Run one full block
   python paradigm/semantic_paradigm_live.py \
       --participant-id test_001 \
       --live
   ```

5. **Validation:**
   ```bash
   # Validate triggers in captured BDF file
   python scripts/validate_biosemi_triggers.py \
       --bdf-file data/eeg/sub-test_001_*.bdf \
       --participant-id test_001
   ```

### Step 6: BDF File Integration

**Requirements:**
- Ensure triggers are properly embedded in BDF files
- Verify trigger codes match CSV mirror logs
- Create validation script for BDF trigger verification
- Handle BDF file naming and organization

**File Structure:**
```
data/eeg/
  └── sub-{participant_id}_{timestamp}/
      ├── sub-{participant_id}_{timestamp}_block-{N}.bdf
      └── ...
```

**Validation:**
- Compare BDF triggers against CSV mirror logs
- Verify all trigger codes are present
- Check timing synchronization

### Step 7: Error Handling and Recovery

**Scenarios to Handle:**

1. **Biosemi Connection Failure:**
   - Graceful fallback to simulation mode (with warning)
   - Clear error messages
   - Option to retry connection

2. **Trigger Send Failure:**
   - Log error but continue experiment
   - Mark failed triggers in CSV log
   - Provide summary of trigger failures at end

3. **Data Stream Interruption:**
   - Detect interruption
   - Pause experiment
   - Attempt reconnection
   - Resume or abort based on user choice

4. **Cleanup on Exit:**
   - Always close Biosemi connection
   - Save all data files
   - Reset parallel port
   - Close CSV logs

## Key Files to Create/Modify

### New Files:
1. `paradigm/utils/biosemi_utils.py` - Biosemi connection utilities
2. `paradigm/semantic_paradigm_live.py` - Live experiment variant
3. `scripts/test_biosemi_connection.py` - Connection testing script
4. `scripts/test_biosemi_triggers.py` - Trigger testing script
5. `scripts/validate_biosemi_triggers.py` - BDF trigger validation

### Files to Modify:
1. `paradigm/utils/trigger_utils.py` - Add Biosemi support
2. `paradigm/scripts/run_experiment.py` - Add live mode flags
3. `config/experiment_config.py` - Add Biosemi configuration options

## Testing Checklist

### Pre-Integration Testing:
- [ ] Biosemi connection utility works
- [ ] Trigger handler sends to Biosemi correctly
- [ ] Error handling works for connection failures
- [ ] Cleanup functions properly close connections

### Integration Testing:
- [ ] Short experiment (1 trial) captures data correctly
- [ ] Triggers appear in BDF file
- [ ] Trigger codes match CSV mirror logs
- [ ] Timing synchronization is accurate

### Full Testing:
- [ ] Complete block runs without errors
- [ ] Multiple blocks work correctly
- [ ] Data files are saved properly
- [ ] Validation script confirms trigger alignment

## Documentation Updates Needed

1. **README.md** - Add live experiment instructions
2. **docs/biosemi_integration.md** - Detailed Biosemi setup guide
3. **docs/trigger_mapping.md** - Already complete, verify accuracy
4. **docs/troubleshooting.md** - Add Biosemi-specific issues

## Dependencies

**New Dependencies (if needed):**
- Biosemi SDK/library (check `grasp/paradigm` requirements)
- BDF file reading library (for validation)
- Any additional hardware drivers

**Check:** Review `grasp/paradigm/requirements.txt` or similar for Biosemi dependencies.

## Success Criteria

1. ✅ Biosemi connection established at experiment start
2. ✅ Triggers sent to Biosemi data stream successfully
3. ✅ BDF files contain all trigger codes
4. ✅ Trigger validation confirms alignment with protocol
5. ✅ Error handling works for all failure scenarios
6. ✅ Data organization matches simulation structure
7. ✅ Cleanup functions properly on exit

## Notes

- **Self-Sufficiency:** Do not import from `grasp/paradigm` directly. Copy/adapt code as needed.
- **Backward Compatibility:** Simulation mode must continue to work unchanged.
- **Trigger Protocols:** Follow established patterns from `grasp/paradigm` for Biosemi trigger sending.
- **Data Organization:** Live experiments should use `data/results/` (not `sim_data/sim_results/`).
- **Validation:** All triggers must be validated against protocol, same as simulation.

## Questions to Resolve

1. What Biosemi SDK/library is used in `grasp/paradigm`?
2. What is the exact connection initialization sequence?
3. How are triggers embedded in BDF files?
4. What error codes/messages does Biosemi provide?
5. Are there any Biosemi-specific timing requirements?

## Next Agent Instructions

1. **Review** `grasp/paradigm` project structure and Biosemi integration
2. **Create** `biosemi_utils.py` based on `grasp/paradigm` patterns
3. **Update** `trigger_utils.py` to support Biosemi
4. **Create** `semantic_paradigm_live.py` based on simulation variant
5. **Test** incrementally (connection → triggers → short experiment → full block)
6. **Validate** triggers in BDF files match protocol
7. **Document** any Biosemi-specific requirements or gotchas

Good luck! The simulation variant is solid, so the live integration should be straightforward once Biosemi connection is established.
