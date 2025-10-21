import network
import urequests
import time
import machine
import sys
import random
import ntptime
from machine import RTC, Pin, deepsleep
sys.path.append('/pyboard')
import moist_detector
get_moisture = moist_detector.get_moisture

# WiFi credentials
WIFI_SSID = 'Orange_Swiatlowod_5070'
WIFI_PASSWORD = 'dagonarian186'

# ntfy.sh endpoint
NTFY_URL = 'https://ntfy.sh/dagonarian'

# Timezone offset for Warsaw (CET/CEST)
# CET = UTC+1, CEST = UTC+2
# We'll use UTC+1 as default, but this should be adjusted for daylight saving time
WARSAW_TIMEZONE_OFFSET = 1  # UTC+1 for CET (adjust to 2 for CEST)

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

def sync_time():
    """Synchronize time with NTP server"""
    try:
        print('Synchronizing time with NTP server...')
        ntptime.settime()
        print('Time synchronized successfully!')
        return True
    except Exception as e:
        print(f'Failed to sync time: {e}')
        return False

def get_warsaw_time():
    """Get current Warsaw time"""
    try:
        # Get UTC time
        utc_time = time.time()
        # Add Warsaw timezone offset
        warsaw_time = utc_time + (WARSAW_TIMEZONE_OFFSET * 3600)
        return warsaw_time
    except Exception as e:
        print(f'Error getting Warsaw time: {e}')
        return None

def is_check_time():
    """Check if current time is 8:00 or 20:00 Warsaw time"""
    try:
        warsaw_time = get_warsaw_time()
        if warsaw_time is None:
            return False
        
        # Convert to local time tuple
        local_time = time.localtime(warsaw_time)
        hour = local_time[3]  # tm_hour
        minute = local_time[4]  # tm_min
        
        # Check if it's 8:00 or 20:00 (with 5 minute tolerance)
        return (hour == 8 and minute <= 5) or (hour == 20 and minute <= 5)
    except Exception as e:
        print(f'Error checking time: {e}')
        return False

def calculate_sleep_time():
    """Calculate how long to sleep until next check time"""
    try:
        warsaw_time = get_warsaw_time()
        if warsaw_time is None:
            return 3600  # Default to 1 hour if time sync fails
        
        local_time = time.localtime(warsaw_time)
        current_hour = local_time[3]
        current_minute = local_time[4]
        current_second = local_time[5]
        
        # Calculate seconds until next check time
        if current_hour < 8:
            # Next check is at 8:00
            next_check_hour = 8
            next_check_minute = 0
        elif current_hour < 20:
            # Next check is at 20:00
            next_check_hour = 20
            next_check_minute = 0
        else:
            # Next check is tomorrow at 8:00
            next_check_hour = 8
            next_check_minute = 0
        
        # Calculate seconds until next check
        current_seconds = current_hour * 3600 + current_minute * 60 + current_second
        next_check_seconds = next_check_hour * 3600 + next_check_minute * 60
        
        if next_check_seconds > current_seconds:
            sleep_seconds = next_check_seconds - current_seconds
        else:
            # Next day
            sleep_seconds = (24 * 3600) - current_seconds + next_check_seconds
        
        return sleep_seconds
    except Exception as e:
        print(f'Error calculating sleep time: {e}')
        return 3600  # Default to 1 hour

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

def check_moisture():
    """Check moisture level and send notification if needed"""
    try:
        print('Checking moisture level...')
        
        # Read moisture level
        moisture_value = get_moisture()
        
        if moisture_value is not None:
            # Create timestamp
            warsaw_time = get_warsaw_time()
            if warsaw_time:
                local_time = time.localtime(warsaw_time)
                timestamp_str = f"{local_time[0]}-{local_time[1]:02d}-{local_time[2]:02d} {local_time[3]:02d}:{local_time[4]:02d}:{local_time[5]:02d}"
            else:
                timestamp_str = str(time.time())
            
            status = "WET" if moisture_value == 1 else "DRY"
            
            print(f'[{timestamp_str}] Moisture: {status} (Digital: {moisture_value})')
            
            # Send notification based on status
            if moisture_value == 0:  # DRY - need water
                message = random.choice(need_water)
                print("Plant needs water - sending notification")
            else:  # WET - all fine
                message = random.choice(all_fine)
                print("Plant is well watered - sending notification")
            
            send_notification(message)
            return True
        else:
            print('Failed to read moisture sensor')
            return False
            
    except Exception as e:
        print(f'Error checking moisture: {e}')
        # Send error notification
        error_message = f"❌ Moisture check error: {str(e)}"
        send_notification(error_message)
        return False

def main():
    """Main function - Scheduled moisture monitoring at 8:00 and 20:00 Warsaw time"""
    print('ESP32 Moisture Monitor - Scheduled Checks (8:00 & 20:00 Warsaw)')
    print('=' * 60)
    
    # Connect to WiFi
    if not connect_wifi():
        print('Cannot proceed without WiFi connection')
        # Sleep for 1 hour and try again
        print('Sleeping for 1 hour before retry...')
        machine.deepsleep(3600000)  # 1 hour in milliseconds
        return
    
    # Synchronize time
    if not sync_time():
        print('Failed to sync time, continuing with local time')
    
    # Send startup notification
    try:
        headers = {'Content-Type': 'text/plain'}
        response = urequests.post(NTFY_URL, data='🌱 Moisture Monitor Started - Scheduled Checks at 8:00 & 20:00 Warsaw Time', headers=headers)
        response.close()
    except:
        pass  # Don't fail if notification doesn't work
    
    print('Starting scheduled moisture monitoring...')
    print('Checks will occur at 8:00 and 20:00 Warsaw time')
    print('Device will deep sleep between checks')
    print('-' * 50)
    
    try:
        while True:
            # Check if it's time for a moisture check
            if is_check_time():
                print('It\'s check time! Performing moisture check...')
                
                # Perform moisture check
                check_moisture()
                
                # Calculate sleep time until next check
                sleep_seconds = calculate_sleep_time()
                print(f'Sleeping for {sleep_seconds} seconds until next check...')
                
                # Deep sleep until next check time
                machine.deepsleep(sleep_seconds * 1000)  # Convert to milliseconds
            else:
                # Not check time yet, sleep for 5 minutes and check again
                print('Not check time yet, sleeping for 5 minutes...')
                time.sleep(300)  # 5 minutes
                
    except KeyboardInterrupt:
        print('\nMonitoring stopped by user')
        # Send final status notification
        try:
            headers = {'Content-Type': 'text/plain'}
            response = urequests.post(NTFY_URL, data='🌱 Moisture Monitor Stopped', headers=headers)
            response.close()
        except:
            pass
    except Exception as e:
        print(f'Error in main loop: {e}')
        # Send error notification
        try:
            error_message = f"❌ Moisture monitor error: {str(e)}"
            send_notification(error_message)
        except:
            pass
        # Sleep for 1 hour before retry
        print('Sleeping for 1 hour before retry...')
        machine.deepsleep(3600000)  # 1 hour in milliseconds
    
    print('Moisture monitoring ended')

# Run the main function
if __name__ == '__main__':
    main()

