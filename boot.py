# boot.py -- run on boot-up
# This file is executed on every boot (including wake-boot from deepsleep)

import esp
import gc

# Disable ESP32 debug output
esp.osdebug(None)

# Run garbage collection
gc.collect()

print("ESP32 booted successfully!")
print("Ready to run main.py...")
