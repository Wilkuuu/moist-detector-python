# ESP32 MicroPython Flashing Guide

## Current Status
- ✅ ESP32 is connected at `/dev/ttyACM0`
- ✅ MicroPython firmware downloaded (`esp32-firmware.bin`)
- ✅ Code files ready (`main.py`, `boot.py`)
- ✅ Virtual environment with esptool v5.1.0 configured
- ✅ Flashing process working (firmware partially flashed)

## Working Flashing Steps

### Step 1: Fix Permissions (if needed)
Open a terminal and run:
```bash
sudo chmod 666 /dev/ttyACM0
```

### Step 2: Flash MicroPython Firmware
**IMPORTANT**: Use the esptool from the virtual environment to avoid compatibility issues:

```bash
cd /home/wilk/Desktop/Projects/moist-detector-python
source venv/bin/activate
./venv/bin/esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write-flash -z 0x1000 esp32-firmware.bin
```

**Note**: The `write-flash` command (with hyphen) is the modern syntax. The old `write_flash` (with underscore) is deprecated.

### Step 3: Upload Code Files
```bash

rshell --port /dev/ttyUSB0
cp main.py /pyboard/
cp moist_detector.py /pyboard/
```

Then in rshell:
```
> repl
> exec(open('main.py').read())
```

## What the Code Does
1. Connects to WiFi: `Orange_Swiatlowod_5070` (password: `dagonarian186`)
2. Sends HTTP POST request to: `https://ntfy.sh/dagonarian`
3. Message: "Hi"

## Troubleshooting

### Common Flashing Issues:

#### "No such file or directory: stub_flasher_32.json"
**Solution**: Use the esptool from the virtual environment instead of the system esptool:
```bash
./venv/bin/esptool.py  # ✅ Correct
esptool                # ❌ Wrong (system version)
```

#### "Chip stopped responding" / "StopIteration"
**Solution**: The firmware was partially flashed. Try these steps:
1. Put ESP32 in bootloader mode:
   - Hold BOOT button
   - Press and release RESET button
   - Release BOOT button
2. Try flashing again with the same command
3. If still failing, try a lower baud rate: `--baud 115200`

#### Permission denied on /dev/ttyACM0
**Solution**: Fix permissions:
```bash
sudo chmod 666 /dev/ttyACM0
# Or add user to dialout group permanently:
sudo usermod -a -G dialout $USER
# Then logout and login again
```

### If upload fails:
1. Check ESP32 is running MicroPython (should show `>>>` prompt)
2. Try different baud rate: `--baud 115200`
3. Check USB cable supports data transfer
4. Verify the port: `ls /dev/tty*`

### If WiFi connection fails:
1. Verify SSID and password are correct
2. Check WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
3. Check signal strength

## Expected Output

### Successful Flashing:
```
esptool v5.1.0
Serial port /dev/ttyACM0:
Connecting....
Connected to ESP32 on /dev/ttyACM0:
Chip type:          ESP32-D0WDQ6 (revision v1.0)
Features:           Wi-Fi, BT, Dual Core + LP Core, 240MHz, Vref calibration in eFuse, Coding Scheme None
Crystal frequency:  40MHz
MAC:                b4:e6:2d:8d:6b:9d

Uploading stub flasher...
Running stub flasher...
Stub flasher running.
Changing baud rate to 460800...
Changed.

Configuring flash size...
Flash will be erased from 0x00001000 to 0x001a8fff...
Compressed 1734416 bytes to 1137589...
Writing at 0x00001000 [============================] 100% (1137589/1137589) bytes...

Hash of data verified.

Leaving...
Hard resetting via RTS pin...
```

### Successful Code Execution:
When working correctly, you should see:
```
ESP32 MicroPython Moisture Monitor
==================================
Connecting to WiFi...
................
WiFi connected successfully!
Network config: ('192.168.1.100', '255.255.255.0', '192.168.1.1', '8.8.8.8')
Starting moisture monitoring...
[1234567890.123] Moisture: 2048
[1234567895.123] Moisture: 1956
```

