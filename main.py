import network
import urequests
import time
import machine
import sys
import random
sys.path.append('/pyboard')
import moist_detector
get_moisture = moist_detector.get_moisture

# WiFi credentials
WIFI_SSID = 'Orange_Swiatlowod_5070'
WIFI_PASSWORD = 'dagonarian186'

# ntfy.sh endpoint
NTFY_URL = 'https://ntfy.sh/dagonarian'

# Message lists for different moisture states
need_water = [
    "Proszę podlej mnie, usycham!",
    "Wooody woooody!",
    "Klaudia, umieraaaam z pragnienia!",
    "SOS! Mayday! Potrzebuję H2O!",
    "Moje liście opadają... dosłownie!",
    "Jestem suchy jak pustynny kaktus (a nie jestem kaktusem!)",
    "Wodaaaa! Daj mi wodaaaa!",
    "Klaudia ratunku! Zaraz się rozsypię!",
    "💧 dramatyczny szept 💧 woda... woda...",
    "Mógłbym wypić cały ocean! No dobra, pół szklanki wystarczy",
    "Jestem bardziej spragniony niż maraton w sierpniu!",
    "Klaudia, pamiętasz o mnie? Bo ja pamiętam o wodzie...",
    "Alarm! Alarm! Poziom wody krytycznie niski!",
    "Moje korzenie organizują protest! Chcą wody!",
    "Więdnę pięknie, ale wolałbym nie więdnąć wcale",
    "NAPÓJ MNIE! Jestem jak gąbka, tylko bez wody",
    "Klaudia? To ja, Twój umierający kwiatek...",
    "Woda jest wszystkim czego potrzebuję... i trochę słońca",
    "Ratuj! Zaczynam przypominać suszone zioła!",
    "Halo? 112? Potrzebuję pilnie wody! Aha, to Ty Klaudia? IDEALNIE!"
]

all_fine = [
    "Dziękuję! Jesteś moją bohaterką!",
    "Pamiętałaś o mnie! Cudownie!",
    "Ahhh, przepyszna woda! Dziękuję!",
    "Jesteś najlepsza Klaudia!",
    "Czuję jak wracam do życia! Dzięki!",
    "Mmm, pyszne! Dokładnie tego potrzebowałem!",
    "Moje liście już się prostują! Dziękuuuję!",
    "Jesteś aniołem z konewką! 😊",
    "Tak bardzo Ci dziękuję! Czuję się o niebo lepiej!",
    "Wiedziałem, że na Ciebie mogę liczyć!",
    "Hurra! Woda! Jesteś wspaniała Klaudia!",
    "Dziękuję za uratowanie mojego życia! (dosłownie!)",
    "Mmm, orzeźwiające! To było dokładnie to czego chciałem!",
    "Jesteś najlepszą opiekunką jaką mógłbym mieć!",
    "Dziękuję! Moje korzenie tańczą z radości!",
    "Cudownie! Czuję się jak nowo narodzony!",
    "Klaudia, jesteś perfekcyjna! Dziękuję za wodę!",
    "Ahhh, ulgaaa! Bardzo Ci dziękuję!",
    "To była najlepsza woda ever! Dzięki!",
    "Kocham Cię Klaudia! (w kwiatowy sposób oczywiście!)"
]

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

def send_notification(message):
    """Send notification to ntfy.sh"""
    try:
        print(f'Sending notification: {message}')
        
        # Prepare the request
        headers = {
            'Content-Type': 'text/plain'
        }
        
        # Send POST request to ntfy.sh
        response = urequests.post(NTFY_URL, data=message, headers=headers)
        
        if response.status_code == 200:
            print('Notification sent successfully!')
        else:
            print(f'Failed to send notification. Status code: {response.status_code}')
        
        response.close()
        
    except Exception as e:
        print(f'Error sending notification: {e}')

def main():
    """Main function - Continuous moisture monitoring every 5 seconds"""
    print('ESP32 Moisture Monitor - 5 Second Intervals')
    print('=' * 45)
    
    # Connect to WiFi
    if not connect_wifi():
        print('Cannot proceed without WiFi connection')
        return
    
    print('Starting moisture monitoring...')
    print('Press Ctrl+C to stop')
    print('-' * 30)
    
    # Track previous status for change detection
    previous_status = None
    reading_count = 0
    
    try:
        while True:
            # Read moisture level
            moisture_value = get_moisture()
            
            if moisture_value is not None:
                # Create timestamp
                timestamp = time.time()
                status = "WET" if moisture_value == 1 else "DRY"
                reading_count += 1
                
                print(f'[{timestamp}] Moisture: {status} (Digital: {moisture_value}) - Reading #{reading_count}')
                
                # Send notification on status change or every 10 readings
                if previous_status != status or reading_count % 10 == 0:
                    if previous_status != status:
                        # Status changed - send random message based on new status
                        if moisture_value == 0:  # WET - need water
                            message = random.choice(all_fine)
                            print(f"Status changed from {previous_status} to {status} - sending need water message")
                        else:  # DRY - all fine
                            message = random.choice(need_water)
                            print(f"Status changed from {previous_status} to {status} - sending all fine message")
                    else:
                        # Periodic update - send random message based on current status
                        if moisture_value == 0:  # WET - need water
                            message = random.choice(all_fine)
                            print(f"Periodic update - sending need water message")
                        else:  # DRY - all fine
                            message = random.choice(need_water)
                            print(f"Periodic update - sending all fine message")
                    
                    send_notification(message)
                
                previous_status = status
            else:
                print('Failed to read moisture sensor')
            
            # Wait 5 seconds before next reading
            time.sleep(5)
            
    except KeyboardInterrupt:
        print('\nMonitoring stopped by user')
        # Send final status notification
        if previous_status is not None:
            if previous_status == 'WET':
                final_message = random.choice(all_fine)
            else:
                final_message = random.choice(need_water)
            send_notification(final_message)
    except Exception as e:
        print(f'Error in main loop: {e}')
        # Send error notification
        error_message = f"❌ Moisture monitor error: {str(e)}"
        send_notification(error_message)
    
    print('Moisture monitoring ended')

# Run the main function
if __name__ == '__main__':
    main()

