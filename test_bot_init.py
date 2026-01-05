#!/usr/bin/env python3
"""Test bot initialization"""
import os
import json
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load config
CONFIG_PATH = os.getenv("BOT_CONFIG_PATH", "config.json")
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

XRAY_CONFIG_PATH = config.get('xray', {}).get('config_path')
XRAY_API_PORT = config.get('xray', {}).get('api_port', 10085)

print(f"Config loaded from: {CONFIG_PATH}")
print(f"XRAY_CONFIG_PATH: {XRAY_CONFIG_PATH}")
print(f"XRAY_API_PORT: {XRAY_API_PORT}")

XRAY_INIT_ERROR = None

try:
    from xray_manager import XrayManager
    xray = XrayManager(config_path=XRAY_CONFIG_PATH or None, api_port=XRAY_API_PORT)
    logger.info(f"XrayManager initialized: config_path={xray.config_path}, api_port={xray.api_port}")
    print("✓ XrayManager initialized successfully")

    # Check available inbounds
    inbounds = xray.get_available_inbounds()
    print(f"\nAvailable inbounds ({len(inbounds)}):")
    for ib in inbounds:
        print(f"  - {ib}")

    # Try to create a trial account
    print("\n  Testing trial account creation...")
    import uuid as uuid_lib
    from datetime import datetime

    trial_uuid = str(uuid_lib.uuid4())
    trial_email = f"trial_vmess_123456_{datetime.now().timestamp()}"

    result, error = xray.add_client('vmess', trial_email, trial_uuid, 'ws')

    if result:
        print(f"  ✓ Trial account created successfully")
        print(f"    UUID: {result['uuid']}")
        print(f"    Email: {result['email']}")
        print(f"    Inbound: {result['inbound_tag']}")

        # Generate link
        SERVER_HOST = config.get('server', {}).get('domain') or config.get('server', {}).get('ip') or '127.0.0.1'
        link = xray.generate_link('vmess', result['uuid'], result['email'], 'ws', SERVER_HOST)
        print(f"    Link: {link[:50]}...")

        # Clean up - remove the test account
        removed = xray.remove_client(trial_email)
        print(f"  ✓ Test account removed: {removed}")
    else:
        print(f"  ✗ Failed to create trial: {error}")

except Exception as e:
    XRAY_INIT_ERROR = str(e)
    logger.critical(f"FATAL: Failed to initialize XrayManager: {e}")
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
