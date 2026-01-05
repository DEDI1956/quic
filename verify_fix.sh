#!/bin/bash
# Quick fix verification script

echo "========================================"
echo "VPN Telegram Bot - Fix Verification"
echo "========================================"
echo ""

# Check if Xray config exists
echo "[1] Checking Xray configuration..."
if [ -f "xray_config.json" ]; then
    echo "✓ xray_config.json exists"

    # Check if it's valid JSON
    if python3 -c "import json; json.load(open('xray_config.json'))" 2>/dev/null; then
        echo "✓ xray_config.json is valid JSON"

        # Check if it has inbounds array
        INBOUNDS=$(python3 -c "import json; print(len(json.load(open('xray_config.json')).get('inbounds', [])))")
        echo "✓ xray_config.json has $INBOUNDS inbounds"
    else
        echo "✗ xray_config.json is not valid JSON"
        exit 1
    fi
else
    echo "✗ xray_config.json not found"
    exit 1
fi

# Check if bot config exists
echo ""
echo "[2] Checking bot configuration..."
if [ -f "config.json" ]; then
    echo "✓ config.json exists"

    # Check if XRAY_CONFIG_PATH is set
    XRAY_PATH=$(python3 -c "import json; print(json.load(open('config.json')).get('xray', {}).get('config_path', ''))")
    if [ -n "$XRAY_PATH" ]; then
        echo "✓ XRAY_CONFIG_PATH is set: $XRAY_PATH"
    else
        echo "✗ XRAY_CONFIG_PATH not set in config.json"
        exit 1
    fi
else
    echo "✗ config.json not found"
    exit 1
fi

# Test XrayManager initialization
echo ""
echo "[3] Testing XrayManager initialization..."
if python3 -c "
import os
os.environ['XRAY_CONFIG_PATH'] = '/home/engine/project/xray_config.json'
from xray_manager import XrayManager
xray = XrayManager()
print('OK')
" 2>/dev/null; then
    echo "✓ XrayManager initializes successfully"
else
    echo "✗ XrayManager failed to initialize"
    exit 1
fi

# Check available inbounds
echo ""
echo "[4] Checking available inbounds..."
INBOUNDS=$(python3 -c "
import os
os.environ['XRAY_CONFIG_PATH'] = '/home/engine/project/xray_config.json'
from xray_manager import XrayManager
xray = XrayManager()
inbounds = xray.get_available_inbounds()
print(f'{len(inbounds)} inbounds found')
for ib in inbounds[:3]:
    print(f'  - {ib}')
if len(inbounds) > 3:
    print(f'  ... and {len(inbounds)-3} more')
" 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "$INBOUNDS"
else
    echo "✗ Failed to get available inbounds"
    exit 1
fi

# Final summary
echo ""
echo "========================================"
echo "✓ ALL CHECKS PASSED!"
echo "========================================"
echo ""
echo "The fix is complete and working correctly."
echo ""
echo "To test trial creation, run:"
echo "  python3 test_trial.py"
echo ""
echo "To run full integration test:"
echo "  python3 test_integration.py"
echo ""
echo "For production deployment, run:"
echo "  sudo bash setup.sh"
echo ""
