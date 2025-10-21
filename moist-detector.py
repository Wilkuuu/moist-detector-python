from machine import Pin
import time

# Configuration
MOISTURE_PIN = 34  # Digital pin for moisture sensor


def get_moisture():
    """Read and return digital moisture value (0=dry, 1=wet)"""
    try:
        # Configure as analog input (since we're getting 4095/0 values)
        from machine import ADC
        adc = ADC(Pin(MOISTURE_PIN))
        adc.atten(ADC.ATTN_11DB)  # Full range: 0-3.3V
        adc.width(ADC.WIDTH_12BIT)  # 0-4095 range
        
        # Take multiple readings for stability
        readings = []
        for _ in range(5):
            readings.append(adc.read())
            time.sleep_ms(100)

        # Get average reading
        avg_reading = sum(readings) // len(readings)
        
        # Convert analog to digital: 4095 = WET, 0 = DRY
        # Use threshold of 2047 (middle value)
        is_wet = avg_reading > 2047
        
        if is_wet:
            print(f'Moisture level: WET (1) - Raw: {avg_reading}')
            return 1
        else:
            print(f'Moisture level: DRY (0) - Raw: {avg_reading}')
            return 0
            
    except Exception as e:
        print(f'Error reading moisture sensor: {e}')
        return None


# Test mode - only runs if executed directly
if __name__ == '__main__':
    print('Moisture Detector Test Mode')
    print('Reading from GPIO34...')
    print('-' * 30)

    while True:
        value = get_moisture()
        time.sleep(1)