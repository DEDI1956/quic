#!/usr/bin/env python3
"""Test XrayManager initialization"""
import os
import sys

# Set the config path before importing XrayManager
os.environ['XRAY_CONFIG_PATH'] = '/home/engine/project/xray_config.json'

from xray_manager import XrayManager

try:
    xray = XrayManager()
    print('✓ XrayManager initialized successfully')
    print(f'  Config path: {xray.config_path}')
    print(f'  API port: {xray.api_port}')

    # Check inbounds
    inbounds = xray.get_available_inbounds()
    print(f'  Available inbounds: {len(inbounds)}')
    for ib in inbounds:
        print(f'    - {ib}')

    # Check health
    healthy, msg = xray.check_health()
    print(f'  Health check: {healthy}')
    print(f'  Health message: {msg}')

    # Try to add a test client
    print('\n  Testing add_client...')
    result, error = xray.add_client('vmess', 'test@example.com', None, 'ws')
    if result:
        print('  ✓ Test client added successfully')
        print(f'    UUID: {result["uuid"]}')
        print(f'    Inbound: {result["inbound_tag"]}')

        # Remove the test client
        removed = xray.remove_client('test@example.com')
        print(f'  ✓ Test client removed: {removed}')
    else:
        print(f'  ✗ Failed to add test client: {error}')

except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
