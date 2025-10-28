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
# NTFY_URL = 'https://ntfy.sh/testmoist'

# Timezone offset for Warsaw (CET/CEST)
# CET = UTC+1, CEST = UTC+2
# We'll use UTC+1 as default, but this should be adjusted for daylight saving time
WARSAW_TIMEZONE_OFFSET = 1  # UTC+1 for CET (adjust to 2 for CEST)

# Message lists for different moisture states
need_water = [
    "Prosze podlej mnie, usycham!",
    "Wooody woooody!",
    "Klaudia, umieraaaam z pragnienia!",
    "SOS! Mayday! Potrzebuje H2O!",
    "Moje liscie opadaja... doslownie!",
    "Jestem suchy jak pustynny kaktus (a nie jestem kaktusem!)",
    "Wodaaaa! Daj mi wodaaaa!",
    "Klaudia ratunku! Zaraz sie rozsypie!",
    "* dramatyczny szept * woda... woda...",
    "Moglem wypic caly ocean! No dobra, pol szklanki wystarczy",
    "Jestem bardziej spragniony niz maraton w sierpniu!",
    "Klaudia, pamietasz o mnie? Bo ja pamietam o wodzie...",
    "Alarm! Alarm! Poziom wody krytycznie niski!",
    "Moje korzenie organizuja protest! Chca wody!",
    "Wiedne pieknie, ale wolalbym nie wiednac wcale",
    "NAPOJ MNIE! Jestem jak gabka, tylko bez wody",
    "Klaudia? To ja, Twoj umierajacy kwiatek...",
    "Woda jest wszystkim czego potrzebuje... i troche slonca",
    "Ratuj! Zaczynam przypominac suszone ziola!",
    "Halo? 112? Potrzebuje pilnie wody! Aha, to Ty Klaudia? IDEALNIE!"
]

very_wet = [
    "Jestem bardzo wilgotny! Dziekuje za doskonała opieke!",
    "Woda? Mam jej pod dostatkiem! Jestem szczesliwy!",
    "Czuje sie swietnie, jestem bardzo dobrze nawodniony!",
    "Klaudia, jestes mistrzynia nawadniania!",
    "Moje korzenie sa zachwycone! Dziekuje!",
    "Wilgotnosc idealna! Jestem wniebowziety!",
    "To byl mistrzowski podlewanie! Dziekuje!",
    "Czuje sie jak w raju wodnym!",
    "Klaudia, moja wilgotnosciowa bohaterko!",
    "Moglibysmy cale lata bez dodatkowej wody!"
]

all_fine = [
    "Dziekuje! Jestes moja bohaterka!",
    "Pamietalas o mnie! Cudownie!",
    "Ahhh, przepyszna woda! Dziekuje!",
    "Jestes najlepsza Klaudia!",
    "Czuje jak wracam do zycia! Dzieki!",
    "Mmm, pyszne! Dokladnie tego potrzebowalem!",
    "Moje liscie juz sie prostuja! Dziekuuuje!",
    "Jestes aniolem z konewka! :-)",
    "Tak bardzo Ci dziekuje! Czuje sie o niebo lepiej!",
    "Wiedzialem, ze na Ciebie moge liczyc!",
    "Hurra! Woda! Jestes wspaniala Klaudia!",
    "Dziekuje za uratowanie mojego zycia! (doslownie!)",
    "Mmm, orzezwiajace! To bylo dokladnie to czego chcialem!",
    "Jestes najlepsza opiekunka jaka moglem miec!",
    "Dziekuje! Moje korzenie tancza z radosci!",
    "Cudownie! Czuje sie jak nowo narodzony!",
    "Klaudia, jestes perfekcyjna! Dziekuje za wode!",
    "Ahhh, ulgaaa! Bardzo Ci dziekuje!",
    "To byla najlepsza woda ever! Dzieki!",
    "Kocham Cie Klaudia! (w kwiatowy sposob oczywiscie!)"
]

getting_dry = [
    "Powoli sie susze... moze troche wody?",
    "Czuje sie coraz bardziej suchy...",
    "Klaudia, pomału przydalaby mi sie woda!",
    "Wilgotnosc spada... obserwuj mnie prosze!",
    "Zaczynam zauwazac deficyt wody...",
    "Moje liscie mowia: 'woda bylaby fajna'",
    "Jestem w porzadku, ale woda bylaby mile widziana!",
    "Coraz bardziej sucho... ale jeszcze jest ok!",
    "Klaudia, nie rozpaczaj, ale pamiętaj o mnie!",
    "Wilgotnosc maleje, ale trzymam sie!"
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
        print(f'Current Warsaw time: {warsaw_time}')
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
        print(f'hour: {hour}:{minute}')
        return True
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

def send_notification(message, moisture_level=None):
    """Send notification to ntfy.sh"""
    try:
        print(f'Sending notification: {message}')

        # Prepare the request
        headers = {
            'Content-Type': 'text/plain'
        }
        
        # Add enhanced headers based on moisture level
        if moisture_level == 3:  # Very Dry - urgent
            headers["Title"] = "Dzbanek!"
            headers["Priority"] = "urgent"
            headers["Tags"] = "warning,skull"
        elif moisture_level == 2:  # Dry - warning
            headers["Title"] = "Roślina się suszy"
            headers["Priority"] = "default"
            headers["Tags"] = "droplet"
        elif moisture_level == 1:  # Wet - all good
            headers["Title"] = "Wszystko OK"
            headers["Priority"] = "default"
            headers["Tags"] = "white_check_mark"
        elif moisture_level == 0:  # Very Wet - excellent
            headers["Title"] = "Doskonale!"
            headers["Priority"] = "default"
            headers["Tags"] = "white_check_mark,heart"

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

        # Read moisture level (0-3: Very Wet, Wet, Dry, Very Dry)
        moisture_level = get_moisture()
        print(f'Moisture level: {moisture_level}')
        if moisture_level is not None:
            # Create timestamp
            warsaw_time = get_warsaw_time()
            if warsaw_time:
                local_time = time.localtime(warsaw_time)
                timestamp_str = f"{local_time[0]}-{local_time[1]:02d}-{local_time[2]:02d} {local_time[3]:02d}:{local_time[4]:02d}:{local_time[5]:02d}"
            else:
                timestamp_str = str(time.time())

            # Map moisture level to status string
            status_map = {
                0: "Very Wet",
                1: "Wet", 
                2: "Dry",
                3: "Very Dry"
            }
            status = status_map.get(moisture_level, "Unknown")

            print(f'[{timestamp_str}] Moisture: {status} (Level: {moisture_level})')

            # Send notification based on moisture level
            if moisture_level == 0:  # Very Wet - all fine
                message = random.choice(very_wet)
                print("Plant is very well watered - sending notification")
                send_notification(message, moisture_level=0)
            elif moisture_level == 1:  # Wet - all fine
                message = random.choice(all_fine)
                print("Plant is well watered - sending notification")
                send_notification(message, moisture_level=1)
            elif moisture_level == 2:  # Dry - getting thirsty
                message = random.choice(getting_dry)
                print("Plant is getting dry - sending notification")
                send_notification(message, moisture_level=2)
            else:  # Very Dry - urgent
                message = random.choice(need_water)
                print("Plant urgently needs water - sending notification")
                send_notification(message, moisture_level=3)

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
    # try:
    #     headers = {'Content-Type': 'text/plain'}
    #     response = urequests.post(NTFY_URL, data='🌱 Moisture Monitor Started - Scheduled Checks at 8:00 & 20:00 Warsaw Time', headers=headers)
    #     response.close()
    # except:
    #     pass  # Don't fail if notification doesn't work

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
                time.sleep(60)  # 5 minutes

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

