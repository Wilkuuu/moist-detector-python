from time import sleep

import network
import urequests
import time
import machine

# WiFi credentials
WIFI_SSID = 'Orange_Swiatlowod_5070'
WIFI_PASSWORD = 'dagonarian186'

# ntfy.sh endpoint
NTFY_URL = 'https://ntfy.sh/dagonarian'

def connect_wifi():
    """Connect to WiFi network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Wait for connection with timeout
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
            print('.', end='')
        
        if wlan.isconnected():
            print('\nWiFi connected successfully!')
            print('Network config:', wlan.ifconfig())
            return True
        else:
            print('\nFailed to connect to WiFi')
            return False
    else:
        print('Already connected to WiFi')
        print('Network config:', wlan.ifconfig())
        return True

def send_notification():
    """Send notification to ntfy.sh"""
    try:
        print('Sending notification to ntfy.sh...')
        
        # Prepare the request
        headers = {
            'Content-Type': 'text/plain'
        }
        
        # Send POST request to ntfy.sh
        response = urequests.post(NTFY_URL, data="Hi", headers=headers)
        
        if response.status_code == 200:
            print('Notification sent successfully!')
        else:
            print(f'Failed to send notification. Status code: {response.status_code}')
        
        response.close()
        
    except Exception as e:
        print(f'Error sending notification: {e}')

def main():
    """Main function"""
    print('ESP32 MicroPython ntfy.sh Notification Sender')
    print('=' * 40)
    
    # Connect to WiFi
    while True:
        if connect_wifi():
            # Send notification
            send_notification()
            sleep(5)
        else:
            print('Cannot proceed without WiFi connection')
            return

        print('Task completed!')
        print('You can reset the ESP32 to run again.')

# Run the main function
if __name__ == '__main__':
    main()
