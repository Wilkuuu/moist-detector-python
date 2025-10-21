# ESP32 MicroPython Flashing Guide

## Current Status
- ✅ ESP32 is connected at `/dev/ttyACM0`
- ✅ MicroPython firmware downloaded (`esp32-firmware.bin`)
- ✅ Code files ready (`main.py`, `boot.py`)
- ❌ Permission issues preventing direct flashing

## Manual Flashing Steps

### Step 1: Fix Permissions
Open a terminal and run:
```bash
sudo chmod 666 /dev/ttyACM0
```

### Step 2: Flash MicroPython Firmware
```bash
cd /home/wilk/Desktop/Projects/esp-moist-python
source venv/bin/activate
esptool --chip esp32 --port /dev/ttyACM0 --baud 460800 write_flash -z 0x1000 esp32-firmware.bin
```

### Step 3: Upload Code Files
```bash
# Upload boot.py
ampy --port /dev/ttyACM0 put boot.py

# Upload main.py
ampy --port /dev/ttyACM0 put main.py
```

### Step 4: Run the Code
```bash
# Connect to ESP32 REPL
ampy --port /dev/ttyACM0 run main.py
```

## Alternative: Using rshell
If ampy doesn't work, try rshell:
```bash
pip install rshell
rshell -p /dev/ttyACM0
```

Then in rshell:
```
> cp boot.py /pyboard/
> cp main.py /pyboard/
> repl
```

## What the Code Does
1. Connects to WiFi: `Orange_Swiatlowod_5070` (password: `dagonarian186`)
2. Sends HTTP POST request to: `https://ntfy.sh/dagonarian`
3. Message: "Hi"

## Troubleshooting

### If flashing fails:
1. Put ESP32 in bootloader mode:
   - Hold BOOT button
   - Press and release RESET button
   - Release BOOT button
2. Try flashing again

### If upload fails:
1. Check ESP32 is running MicroPython (should show `>>>` prompt)
2. Try different baud rate: `--baud 115200`
3. Check USB cable supports data transfer

### If WiFi connection fails:
1. Verify SSID and password are correct
2. Check WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
3. Check signal strength

## Expected Output
When working correctly, you should see:
```
ESP32 MicroPython ntfy.sh Notification Sender
========================================
Connecting to WiFi...
................
WiFi connected successfully!
Network config: ('192.168.1.100', '255.255.255.0', '192.168.1.1', '8.8.8.8')
Sending notification to ntfy.sh...
Notification sent successfully!
Task completed!
```
