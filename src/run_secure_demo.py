#!/usr/bin/env python3
"""
Quick launcher for the Secure Compliance Filter Demo
"""

import os
import sys

def main():
    """Run the authenticated demo"""
    print("🔐 Starting Secure Compliance Filter Demo...")
    
    # Change to src directory
    src_dir = os.path.dirname(__file__)
    if src_dir:
        os.chdir(src_dir)
    
    # Add src to Python path
    sys.path.insert(0, os.getcwd())
    
    try:
        from authenticated_demo_ui import main as run_demo
        run_demo()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install flask PyJWT pyotp qrcode[pil] requests")
        return 1
    except Exception as e:
        print(f"❌ Error starting demo: {e}")
        return 1

if __name__ == '__main__':
    exit(main())