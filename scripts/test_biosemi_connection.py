#!/usr/bin/env python3
"""
Test Biosemi connection.

Tests serial port connection to Biosemi hardware without running an experiment.
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from paradigm.utils import connect_biosemi, verify_biosemi_connection, close_biosemi_connection


def test_connection(port: str = 'COM3'):
    """
    Test Biosemi connection.
    
    Parameters
    ----------
    port : str
        Serial port name
    
    Returns
    -------
    bool
        True if connection successful, False otherwise
    """
    print("="*70)
    print("BIOSEMI CONNECTION TEST")
    print("="*70)
    print(f"Testing connection to {port}...")
    print()
    
    biosemi_conn = None
    try:
        biosemi_conn = connect_biosemi(port=port)
        
        if verify_biosemi_connection(biosemi_conn):
            print(f"[OK] Biosemi connected successfully to {port}")
            print(f"[OK] Connection verified and ready")
            close_biosemi_connection(biosemi_conn)
            return True
        else:
            print(f"[FAIL] Biosemi connection verification failed")
            if biosemi_conn:
                close_biosemi_connection(biosemi_conn)
            return False
            
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        if biosemi_conn:
            close_biosemi_connection(biosemi_conn)
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Test Biosemi serial port connection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test default port (COM3)
  python scripts/test_biosemi_connection.py
  
  # Test specific port
  python scripts/test_biosemi_connection.py --port COM4
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        type=str,
        default='COM3',
        help='Serial port for Biosemi (default: COM3)'
    )
    
    args = parser.parse_args()
    
    success = test_connection(port=args.port)
    
    if success:
        print("\n[SUCCESS] Biosemi connection test passed!")
        sys.exit(0)
    else:
        print("\n[FAILURE] Biosemi connection test failed!")
        sys.exit(1)
