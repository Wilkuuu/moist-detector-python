# ESP32 MicroPython Moisture Monitor

This project demonstrates how to use an ESP32 with a moisture sensor to continuously monitor soil moisture levels and optionally send notifications via ntfy.sh service.

## Features

- Connects to WiFi network automatically
- Continuous moisture monitoring every 5 seconds
- Optional notifications via ntfy.sh
- Error handling and status reporting
- No deep sleep - perfect for testing
- Timestamp logging for each reading

## Hardware Requirements

- ESP32 development board
- Moisture sensor (connected to GPIO34)
- USB cable for programming and power
- Computer with Python and esptool installed

## Software Requirements

- MicroPython firmware for ESP32
- esptool for flashing firmware
- rshell for file transfer and REPL access

## Setup Instructions

### 1. Flash MicroPython Firmware

The project includes a pre-downloaded MicroPython firmware file (`esp32-firmware.bin`).

**Important**: Use the esptool from the virtual environment to avoid compatibility issues:

```bash
cd /home/wilk/Desktop/Projects/moist-detector-python
source venv/bin/activate
./venv/bin/esptool.py --chip esp32 --port /dev/ttyACM0 --baud 460800 write-flash -z 0x1000 esp32-firmware.bin
```

**Note**: 
- Replace `/dev/ttyACM0` with your ESP32's actual port (check with `ls /dev/tty*`)
- The `write-flash` command (with hyphen) is the modern syntax
- If flashing fails, try putting the ESP32 in bootloader mode (hold BOOT button, press RESET, release BOOT)

### 2. Upload Code to ESP32

Using rshell (recommended):
```bash
rshell --port /dev/ttyACM0
# Then inside rshell:
cp main.py /pyboard/
cp moist-detector.py /pyboard/
```

Alternative using ampy:
```bash
ampy --port /dev/ttyACM0 put main.py
ampy --port /dev/ttyACM0 put moist-detector.py
```

### 3. Configure WiFi

Edit `main.py` and update the WiFi credentials:
```python
WIFI_SSID = 'Your_WiFi_SSID'
WIFI_PASSWORD = 'Your_WiFi_Password'
```

### 4. Run the Code

Using rshell:
```bash
rshell --port /dev/ttyACM0
# Then inside rshell:
repl
# In the REPL, run:
exec(open('main.py').read())
```

Or reset the ESP32 - it will automatically run `main.py` on boot.

The moisture monitor will start reading every 5 seconds and display output like:
```
[1234567890.123] Moisture: 2048
[1234567895.123] Moisture: 1956
```

## How It Works

1. **WiFi Connection**: The ESP32 connects to the specified WiFi network
2. **Moisture Reading**: Reads analog value from moisture sensor on GPIO34 every 5 seconds
3. **Data Logging**: Displays timestamp and moisture value for each reading
4. **Optional Notifications**: Can send periodic notifications via ntfy.sh (commented out by default)
5. **Continuous Monitoring**: Runs indefinitely without deep sleep for easy testing

## Code Structure

- `boot.py`: Initialization code that runs on every boot
- `main.py`: Main application code with WiFi connection and continuous moisture monitoring
- `moist-detector.py`: Moisture sensor reading functions
- `requirements.txt`: Lists the built-in modules used (no external dependencies)

## Troubleshooting

### WiFi Connection Issues
- Check SSID and password are correct
- Ensure WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)
- Check signal strength

### Moisture Sensor Issues
- Check sensor is connected to GPIO34
- Verify sensor power supply (3.3V)
- Check for loose connections
- Monitor serial output for sensor errors

### HTTP Request Issues (if using notifications)
- Verify internet connectivity
- Check if ntfy.sh service is accessible
- Monitor serial output for error messages

### Upload Issues
- Ensure correct COM port (check with `ls /dev/tty*`)
- Check ESP32 is in bootloader mode if needed (hold BOOT, press RESET, release BOOT)
- Verify MicroPython firmware is properly flashed
- Use the esptool from the virtual environment: `./venv/bin/esptool.py`
- Try different baud rates if connection fails (115200, 460800)

### Flashing Issues
- **"No such file or directory: stub_flasher_32.json"**: Use the esptool from the virtual environment instead of system esptool
- **"Chip stopped responding"**: The firmware was partially flashed. Try flashing again or put ESP32 in bootloader mode
- **Permission denied**: Run `sudo chmod 666 /dev/ttyACM0` or add your user to the dialout group

## Customization

You can modify the code to:
- Change monitoring interval (currently 5 seconds)
- Adjust moisture sensor pin (currently GPIO34)
- Enable/disable notifications
- Add moisture level thresholds and alerts
- Implement data logging to file
- Add LED indicators for moisture status
- Send different notification messages
- Use different ntfy.sh topics

## License

This project is open source and available under the MIT License.

