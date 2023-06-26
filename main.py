import time
from mqtt import MQTTClient   # For use of MQTT protocol to talk to Adafruit IO
import ubinascii              # Conversions between binary data and various encodings
import machine                # Interfaces with hardware components
import micropython            # Needed to run any MicroPython code
import random                 # Random number generator
from machine import Pin       # Define pin
import utime as time
from dht import DHT11
# from machine import DHT11
import wifi

# The GPIO number is 13 which is equal to the pin number 17
"""
pin = Pin(28, Pin.OUT, Pin.PULL_DOWN)
sensor = DHT11(pin)

while True:
    time.sleep(2)
    try:
        t = sensor.temperature
        time.sleep(2)
        h = sensor.humidity
    except:
        print("An exception occurred")  
        continue  
    print("Temperature testing: {}".format(sensor.temperature))
    print("Humidity: {}".format(sensor.humidity))
"""

# BEGIN SETTINGS
# These need to be change to suit your environment
RANDOMS_INTERVAL = 1000   # milliseconds
last_random_sent_ticks = 0  # milliseconds
led = Pin("LED", Pin.OUT)   # led pin initialization for Raspberry Pi Pico W

# Adafruit IO (AIO) configuration
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = "Paty_Marklund"
AIO_KEY = "aio_MflH12VcW9kHOUl9FAzyjsvY4SlV"
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything
AIO_LIGHTS_FEED = "Paty_Marklund/feeds/lights"
AIO_TEMP_FEED = "Paty_Marklund/feeds/temperature"
AIO_HUMID_FEED = "Paty_Marklund/feeds/humidity"

# END SETTINGS

# FUNCTIONS

# Callback Function to respond to messages from Adafruit IO
def sub_cb(topic, msg):          # sub_cb means "callback subroutine"
    print((topic, msg))          # Outputs the message that was received. Debugging use.
    if msg == b"ON":             # If message says "ON" ...
        led.on()                 # ... then LED on
    elif msg == b"OFF":          # If message says "OFF" ...
        led.off()                # ... then LED off
    else:                        # If any other message is received ...
        print("Unknown message") # ... do nothing but output that it happened.

# Function to generate a random number between 0 and the upper_bound
def random_integer(upper_bound):
    return random.getrandbits(32) % upper_bound

"""
# Function to publish random number to Adafruit IO MQTT server at fixed interval
def send_random():
    global last_random_sent_ticks
    global RANDOMS_INTERVAL

    if ((time.ticks_ms() - last_random_sent_ticks) < RANDOMS_INTERVAL):
        return; # Too soon since last one sent.

    #some_number = random_integer(100)
    print("Publishing: {0} to {1} ... ".format(some_number, AIO_RANDOMS_FEED), end='')
    try:
        client.publish(topic=AIO_RANDOMS_FEED, msg=str(some_number))
        print("DONE")
    except Exception as e:
        print("FAILED")
    finally:
        last_random_sent_ticks = time.ticks_ms()
"""

def get_temperature():
    pin = Pin(28, Pin.OUT, Pin.PULL_DOWN)
    # sensor = DHT11(pin)
    sensor = DHT11(machine.Pin(28))
    global last_random_sent_ticks
    global RANDOMS_INTERVAL

    if ((time.ticks_ms() - last_random_sent_ticks) < RANDOMS_INTERVAL):
        return; # Too soon since last one sent.
    
    while True:
        time.sleep(2)
        try:
            t = sensor.temperature
            time.sleep(2)
            h = sensor.humidity
        except:
            print("An exception occurred")  
            continue  
            
        print("Publishing: {0} to {1} ... ".format(t, AIO_TEMP_FEED), end='')
        print("Publishing: {0} to {1} ... ".format(h, AIO_HUMID_FEED), end='')
        try:
            client.publish(topic=AIO_TEMP_FEED, msg=str(t))
            client.publish(topic=AIO_HUMID_FEED, msg=str(h))
            print("DONE")
        except Exception as e:
            print("FAILED")
        finally:
            last_random_sent_ticks = time.ticks_ms()

# Try WiFi Connection
try:
    ip = wifi.do_connect()
except KeyboardInterrupt:
    print("Keyboard interrupt")

# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(AIO_CLIENT_ID, AIO_SERVER, AIO_PORT, AIO_USER, AIO_KEY)

# Subscribed messages will be delivered to this callback
client.set_callback(sub_cb)
client.connect()
client.subscribe(AIO_LIGHTS_FEED)
print("Connected to %s, subscribed to %s topic" % (AIO_SERVER, AIO_LIGHTS_FEED))



try:                      # Code between try: and finally: may cause an error
                          # so ensure the client disconnects the server if
                          # that happens.
    while 1:              # Repeat this loop forever
        client.check_msg()# Action a message if one is received. Non-blocking.
        get_temperature()
        #send_random()     # Send a random number to Adafruit IO if it's time.
finally:                  # If an exception is thrown ...
    client.disconnect()   # ... disconnect the client and clean up.
    client = None
    print("Disconnected from Adafruit IO.")
    
# TO DO:
    """
    * Code part:
    
    - Find how to connect the display with the board
    - Create code to calculate the temperature and humidity to send a message of the weather
        (either the code will be done on the board or on the dashboard)
    - Send message from dashboard to the display for the weather condition
    - Set up display and display the message
    - Separate methods out of the main()
    - Clean the code
    
    * Theory part 
    
    - Create the template
    - Import code to github
    - Complete Quiz #3
    
    """