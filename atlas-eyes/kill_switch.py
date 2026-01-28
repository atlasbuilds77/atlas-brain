#!/usr/bin/env python3
"""
Atlas Eyes Kill Switch
Emergency disable for camera system
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from security import activate_kill_switch, deactivate_kill_switch, check_kill_switch
import argparse


def main():
    parser = argparse.ArgumentParser(description='Atlas Eyes Emergency Kill Switch')
    parser.add_argument('action', choices=['activate', 'deactivate', 'status'],
                       help='Kill switch action')
    parser.add_argument('--reason', type=str, default='Manual trigger',
                       help='Reason for activation')
    
    args = parser.parse_args()
    
    if args.action == 'activate':
        activate_kill_switch(args.reason)
        print("\n🔴 CAMERA SYSTEM DISABLED")
        print("All camera access terminated.")
        print("Atlas Eyes will not start until kill switch is deactivated.")
        print("\nTo re-enable: python3 kill_switch.py deactivate")
    
    elif args.action == 'deactivate':
        deactivate_kill_switch()
        print("\n✅ CAMERA SYSTEM RE-ENABLED")
        print("Atlas Eyes can now be started normally.")
    
    elif args.action == 'status':
        if check_kill_switch():
            print("🔴 KILL SWITCH ACTIVE - Camera system DISABLED")
            sys.exit(1)
        else:
            print("✅ Kill switch inactive - Camera system operational")
            sys.exit(0)


if __name__ == '__main__':
    main()
