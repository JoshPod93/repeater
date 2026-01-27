#!/usr/bin/env python3
"""
Test Biosemi triggers.

Sends test triggers to Biosemi hardware without running an experiment.
"""

import argparse
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from paradigm.utils.biosemi_utils import (
    open_serial_port, verify_biosemi_connection, close_serial_port,
    send_biosemi_trigger
)


def test_triggers(port: str = None, n_triggers: int = 10, delay: float = 0.1):
    """
    Send test triggers to Biosemi.
    
    Parameters
    ----------
    port : str
        Serial port name
    n_triggers : int
        Number of triggers to send
    delay : float
        Delay between triggers (seconds)
    
    Returns
    -------
    bool
        True if all triggers sent successfully, False otherwise
    """
    print("="*70)
    print("BIOSEMI TRIGGER TEST")
    print("="*70)
    
    # Always use COM4
    port = 'COM4'
    
    print(f"Connecting to {port}...")
    print()
    
    biosemi_conn = None
    try:
        biosemi_conn = open_serial_port(port=port)
        
        if biosemi_conn is None:
            print(f"[FAIL] Failed to open serial port {port}")
            return False
        
        if not verify_biosemi_connection(biosemi_conn):
            print(f"[FAIL] Biosemi connection verification failed")
            if biosemi_conn:
                close_serial_port()
            return False
        
        print(f"[OK] Connected to {port}")
        print(f"[INFO] Sending {n_triggers} test triggers...")
        print()
        
        success_count = 0
        for i in range(n_triggers):
            trigger_code = (i % 255) + 1  # Cycle through codes 1-255
            success = send_biosemi_trigger(trigger_code, f"test_trigger_{i+1}")
            
            if success:
                print(f"  [{i+1:3d}/{n_triggers}] Trigger {trigger_code:3d} sent successfully")
                success_count += 1
            else:
                print(f"  [{i+1:3d}/{n_triggers}] Trigger {trigger_code:3d} FAILED")
            
            # Wait between triggers (except for last one)
            if i < n_triggers - 1:
                time.sleep(delay)
        
        print()
        print(f"[RESULTS] {success_count}/{n_triggers} triggers sent successfully")
        
        close_serial_port()
        
        if success_count == n_triggers:
            print("[SUCCESS] All triggers sent successfully!")
            return True
        else:
            print(f"[WARNING] {n_triggers - success_count} trigger(s) failed")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        if biosemi_conn:
            close_biosemi_connection(biosemi_conn)
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Test Biosemi trigger sending',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send 10 test triggers (default)
  python scripts/test_biosemi_triggers.py
  
  # Send 20 triggers with custom delay
  python scripts/test_biosemi_triggers.py --n-triggers 20 --delay 0.2
  
  # Test specific port
  python scripts/test_biosemi_triggers.py --port COM4
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        type=str,
        default=None,
        help='Serial port for Biosemi (default: COM4 from config)'
    )
    
    parser.add_argument(
        '--n-triggers', '-n',
        type=int,
        default=10,
        help='Number of triggers to send (default: 10)'
    )
    
    parser.add_argument(
        '--delay', '-d',
        type=float,
        default=0.1,
        help='Delay between triggers in seconds (default: 0.1)'
    )
    
    args = parser.parse_args()
    
    success = test_triggers(
        port=args.port,
        n_triggers=args.n_triggers,
        delay=args.delay
    )
    
    if success:
        print("\n[SUCCESS] Biosemi trigger test passed!")
        sys.exit(0)
    else:
        print("\n[FAILURE] Biosemi trigger test failed!")
        sys.exit(1)
