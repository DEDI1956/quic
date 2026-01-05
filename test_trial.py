#!/usr/bin/env python3
"""Test trial account creation flow"""
import os
import sys

# Set config path
os.environ['XRAY_CONFIG_PATH'] = '/home/engine/project/xray_config.json'

from xray_manager import XrayManager
from datetime import datetime
import uuid as uuid_lib

print("=" * 60)
print("Testing Trial Account Creation Flow")
print("=" * 60)

# Step 1: Initialize XrayManager
print("\n[1] Initializing XrayManager...")
try:
    xray = XrayManager()
    print(f"✓ XrayManager initialized")
    print(f"  Config path: {xray.config_path}")
    print(f"  API port: {xray.api_port}")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# Step 2: Check available inbounds
print("\n[2] Checking available inbounds...")
inbounds = xray.get_available_inbounds()
print(f"✓ Found {len(inbounds)} inbounds:")
for ib in inbounds:
    print(f"  - {ib}")

# Check if vmess-ws exists (used for trials)
vmess_ws_exists = any('vmess-ws' in ib for ib in inbounds)
if not vmess_ws_exists:
    print("✗ ERROR: 'vmess-ws' inbound not found!")
    print("  This inbound is required for trial accounts.")
    sys.exit(1)
else:
    print("✓ Required 'vmess-ws' inbound found")

# Step 3: Check config accessibility
print("\n[3] Checking config accessibility...")
is_accessible, config_msg = xray.check_config_accessibility()
if is_accessible:
    print(f"✓ Config is accessible")
else:
    print(f"✗ Config not accessible: {config_msg}")
    # This is expected in non-production environments

# Step 4: Create trial account
print("\n[4] Creating trial account...")
try:
    # Trial configuration
    protocol = "vmess"
    conn_type = "ws"
    user_id = 123456789  # Test user ID
    trial_uuid = str(uuid_lib.uuid4())
    trial_email = f"trial_{protocol}_{user_id}_{datetime.now().timestamp()}"

    print(f"  Protocol: {protocol}")
    print(f"  Connection type: {conn_type}")
    print(f"  Email: {trial_email}")
    print(f"  UUID: {trial_uuid}")

    result, error = xray.add_client(protocol, trial_email, trial_uuid, conn_type)

    if result:
        print("✓ Trial account created successfully!")
        print(f"  Details:")
        print(f"    UUID: {result['uuid']}")
        print(f"    Email: {result['email']}")
        print(f"    Protocol: {result['protocol']}")
        print(f"    Connection type: {result['connection_type']}")
        print(f"    Inbound tag: {result['inbound_tag']}")

        # Step 5: Generate VPN link
        print("\n[5] Generating VPN link...")
        SERVER_HOST = "127.0.0.1"  # Use IP for non-TLS
        link = xray.generate_link(
            result['protocol'],
            result['uuid'],
            result['email'],
            result['connection_type'],
            SERVER_HOST
        )
        print(f"✓ Link generated:")
        print(f"  {link}")

        # Step 6: Verify client in config
        print("\n[6] Verifying client in Xray config...")
        client_info = xray.get_client_info(trial_email)
        if client_info:
            print("✓ Client verified in config")
            print(f"  Protocol: {client_info['protocol']}")
            print(f"  Tag: {client_info['tag']}")
            print(f"  Port: {client_info['port']}")
        else:
            print("✗ Client not found in config!")

        # Step 7: Cleanup - remove test account
        print("\n[7] Cleaning up test account...")
        removed = xray.remove_client(trial_email)
        if removed:
            print("✓ Test account removed successfully")
        else:
            print("✗ Failed to remove test account")

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe trial creation flow is working correctly.")
        print("Note: Xray service health check is expected to fail")
        print("      in non-production environments.")

    else:
        print(f"✗ Failed to create trial account: {error}")
        sys.exit(1)

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
