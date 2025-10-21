#!/bin/bash

echo "Fixing ESP32 permissions and running the code..."
echo "=============================================="

# Fix permissions
echo "1. Fixing permissions..."
sudo chmod 666 /dev/ttyACM0

if [ $? -eq 0 ]; then
    echo "✓ Permissions fixed successfully"
else
    echo "✗ Failed to fix permissions"
    exit 1
fi

# Change to project directory
cd /home/wilk/Desktop/Projects/esp-moist-python

# Activate virtual environment
echo "2. Activating virtual environment..."
source venv/bin/activate

# Check if ESP32 has MicroPython
echo "3. Checking ESP32..."
python3 -c "
import serial
import time

try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
    time.sleep(1)
    ser.write(b'\r\n')
    time.sleep(0.5)
    response = ser.read(200)
    
    if b'MicroPython' in response or b'>>>' in response:
        print('✓ MicroPython detected!')
        
        # Upload and run main.py
        print('4. Uploading and running main.py...')
        with open('main.py', 'r') as f:
            content = f.read()
        
        # Send the code line by line
        lines = content.split('\n')
        for line in lines:
            if line.strip():
                ser.write((line + '\r\n').encode())
                time.sleep(0.1)
        
        # Run the code
        ser.write(b'exec(open(\"main.py\").read())\r\n')
        time.sleep(5)
        
        # Read the response
        response = ser.read(2000)
        print('\\n=== ESP32 OUTPUT ===')
        print(response.decode('utf-8', errors='ignore'))
        print('=== END OUTPUT ===')
        
    else:
        print('✗ No MicroPython detected')
        print('You need to flash MicroPython firmware first')
        print('Run: esptool --chip esp32 --port /dev/ttyACM0 --baud 460800 write_flash -z 0x1000 esp32-firmware.bin')
    
    ser.close()
    
except Exception as e:
    print(f'✗ Error: {e}')
"

echo "Done!"

