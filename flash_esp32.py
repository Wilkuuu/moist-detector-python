#!/usr/bin/env python3
"""
ESP32 MicroPython Flashing and Upload Script
This script helps flash MicroPython firmware and upload code to ESP32
"""

import serial
import time
import sys
import os

def check_esp32_connection(port):
    """Check if ESP32 is connected and accessible"""
    try:
        ser = serial.Serial(port, 115200, timeout=2)
        time.sleep(1)
        ser.write(b'\r\n')
        time.sleep(0.5)
        response = ser.read(100)
        ser.close()
        
        if b'MicroPython' in response or b'>>>' in response:
            print(f"✓ ESP32 found at {port} - MicroPython detected!")
            return True
        else:
            print(f"✓ ESP32 found at {port} - No MicroPython detected")
            return False
    except Exception as e:
        print(f"✗ Cannot access {port}: {e}")
        return False

def upload_code(port, filename):
    """Upload a Python file to ESP32"""
    try:
        print(f"Uploading {filename} to ESP32...")
        
        # Read the file
        with open(filename, 'r') as f:
            content = f.read()
        
        # Connect to ESP32
        ser = serial.Serial(port, 115200, timeout=2)
        time.sleep(1)
        
        # Send the file content
        lines = content.split('\n')
        for line in lines:
            if line.strip():
                ser.write((line + '\r\n').encode())
                time.sleep(0.1)
                response = ser.read(100)
                if b'>>>' not in response:
                    print(f"Warning: Unexpected response: {response}")
        
        ser.close()
        print(f"✓ {filename} uploaded successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error uploading {filename}: {e}")
        return False

def run_code(port):
    """Run the main.py code on ESP32"""
    try:
        print("Running main.py on ESP32...")
        
        ser = serial.Serial(port, 115200, timeout=5)
        time.sleep(1)
        
        # Send command to run main.py
        ser.write(b'exec(open("main.py").read())\r\n')
        time.sleep(2)
        
        # Read response
        response = ser.read(1000)
        print("ESP32 Response:")
        print(response.decode('utf-8', errors='ignore'))
        
        ser.close()
        return True
        
    except Exception as e:
        print(f"✗ Error running code: {e}")
        return False

def main():
    port = '/dev/ttyACM0'
    
    print("ESP32 MicroPython Setup")
    print("=" * 30)
    
    # Check connection
    if not check_esp32_connection(port):
        print("\nPlease check:")
        print("1. ESP32 is connected via USB")
        print("2. Correct port is being used")
        print("3. ESP32 has MicroPython firmware installed")
        print("\nTo flash MicroPython firmware, you'll need to:")
        print("1. Put ESP32 in bootloader mode (hold BOOT button while pressing RESET)")
        print("2. Run: esptool --chip esp32 --port /dev/ttyACM0 --baud 460800 write_flash -z 0x1000 esp32-firmware.bin")
        return
    
    # Upload files
    files_to_upload = ['boot.py', 'main.py']
    for filename in files_to_upload:
        if os.path.exists(filename):
            upload_code(port, filename)
        else:
            print(f"✗ {filename} not found")
    
    # Run the code
    print("\nRunning the notification sender...")
    run_code(port)

if __name__ == '__main__':
    main()
