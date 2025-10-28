from machine import Pin
import time

# Configuration - Using recommended GPIO 36 (ADC0) from ESP32IO tutorial
MOISTURE_PIN = 36  # GPIO36 (ADC0) for moisture sensor


def get_moisture():
    """
    Read and return moisture level (0-3)
    Returns:
        0: Very Wet (soaked)
        1: Wet (moist, good)
        2: Dry (needs water soon)
        3: Very Dry (urgently needs water)
    """
    try:
        # Configure as analog input per ESP32IO recommended setup
        from machine import ADC
        adc = ADC(Pin(MOISTURE_PIN))
        adc.atten(ADC.ATTN_11DB)  # Full range: 0-3.3V (recommended by ESP32IO)
        adc.width(ADC.WIDTH_12BIT)  # 0-4095 range
        
        # Take multiple readings for stability
        readings = []
        for _ in range(5):
            readings.append(adc.read())
            time.sleep_ms(100)
        
        # Get average reading
        avg_reading = sum(readings) // len(readings)
        
        # Per ESP32IO tutorial: Higher value = DRY soil, Lower value = WET soil
        # Defining thresholds for 4 levels based on typical readings
        # Adjust these values based on your calibration
        VERY_WET_THRESHOLD = 1500   # < 1500 = soaked
        WET_THRESHOLD = 2000        # 1500-2000 = moist/good
        DRY_THRESHOLD = 2500        # 2000-2500 = drying out
        
        # Determine moisture level
        if avg_reading < VERY_WET_THRESHOLD:
            level = 0
            status = "Very Wet"
        elif avg_reading < WET_THRESHOLD:
            level = 1
            status = "Wet"
        elif avg_reading < DRY_THRESHOLD:
            level = 2
            status = "Dry"
        else:
            level = 3
            status = "Very Dry"
        
        print(f'Moisture level: {status} ({level}) - Raw: {avg_reading}')
        return level
            
    except Exception as e:
        print(f'Error reading moisture sensor: {e}')
        return None


# Test mode - only runs if executed directly
if __name__ == '__main__':
    print('Moisture Detector Test Mode')
    print('Reading from GPIO36 (ADC0)...')
    print('-' * 30)

    while True:
        value = get_moisture()
        time.sleep(1)