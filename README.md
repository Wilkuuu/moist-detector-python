# ESP32 MicroPython ntfy.sh Notification Sender

This project demonstrates how to connect an ESP32 to WiFi and send notifications using ntfy.sh service.

## Features

- Connects to WiFi network automatically
- Sends HTTP POST request to ntfy.sh
- Error handling and status reporting
- Simple and lightweight code

## Hardware Requirements

- ESP32 development board
- USB cable for programming and power
- Computer with Python and esptool installed

## Software Requirements

- MicroPython firmware for ESP32
- esptool for flashing firmware
- ampy or similar tool for file transfer

## Setup Instructions

### 1. Flash MicroPython Firmware

Download the latest MicroPython firmware for ESP32 from [micropython.org](https://micropython.org/download/esp32/)

Flash the firmware using esptool:
```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-20240105-v1.22.1.bin
```

Replace `/dev/ttyUSB0` with your ESP32's port and `esp32-20240105-v1.22.1.bin` with your firmware file.

### 2. Upload Code to ESP32

Using ampy:
```bash
ampy --port /dev/ttyUSB0 put boot.py
ampy --port /dev/ttyUSB0 put main.py
```

Or using rshell:
```bash
rshell -p /dev/ttyUSB0
> cp boot.py /pyboard/
> cp main.py /pyboard/
```

### 3. Configure WiFi

Edit `main.py` and update the WiFi credentials:
```python
WIFI_SSID = 'Your_WiFi_SSID'
WIFI_PASSWORD = 'Your_WiFi_Password'
```

### 4. Run the Code

Connect to the ESP32 REPL:
```bash
ampy --port /dev/ttyUSB0 run main.py
```

Or reset the ESP32 - it will automatically run `main.py` on boot.

## How It Works

1. **WiFi Connection**: The ESP32 connects to the specified WiFi network
2. **HTTP Request**: Sends a POST request to `https://ntfy.sh/dagonarian` with the message "Hi"
3. **Status Reporting**: Prints connection status and notification results

## Code Structure

- `boot.py`: Initialization code that runs on every boot
- `main.py`: Main application code with WiFi connection and notification sending
- `requirements.txt`: Lists the built-in modules used (no external dependencies)

## Troubleshooting

### WiFi Connection Issues
- Check SSID and password are correct
- Ensure WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)
- Check signal strength

### HTTP Request Issues
- Verify internet connectivity
- Check if ntfy.sh service is accessible
- Monitor serial output for error messages

### Upload Issues
- Ensure correct COM port
- Check ESP32 is in bootloader mode if needed
- Verify MicroPython firmware is properly flashed

## Customization

You can modify the code to:
- Send different messages
- Use different ntfy.sh topics
- Add sensors and send sensor data
- Implement scheduled notifications
- Add LED indicators for status

## License

This project is open source and available under the MIT License.
