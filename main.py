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
from machine import I2C, Pin
from pico_i2c_lcd import I2cLcd


# BEGIN SETTINGS
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=400000)
RANDOMS_INTERVAL = 60   # milliseconds
last_random_sent_ticks = 0  # milliseconds
led = Pin("LED", Pin.OUT)   # led pin initialization for Raspberry Pi Pico W

# Adafruit IO (AIO) configuration
AIO_SERVER = "io.adafruit.com"
AIO_PORT = 1883
AIO_USER = "Paty_Marklund"
AIO_KEY = "aio_YreN52bFpnin2Ctj4BWmRA9Gbhm0"
AIO_CLIENT_ID = ubinascii.hexlify(machine.unique_id()) 
AIO_LIGHTS_FEED = "Paty_Marklund/feeds/lights"
AIO_TEMP_FEED = "Paty_Marklund/feeds/temperature"
AIO_HUMID_FEED = "Paty_Marklund/feeds/humidity"
AIO_MESSAGE_FEED = "Paty_Marklund/feeds/message"

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

def get_temperature():
    pin = Pin(28, Pin.OUT, Pin.PULL_DOWN)
    # sensor = DHT11(pin)
    sensor = DHT11(machine.Pin(28))
    global last_random_sent_ticks
    global RANDOMS_INTERVAL
    prev_temp = None
    prev_humid = None
    
    if ((time.ticks_ms() - last_random_sent_ticks) < RANDOMS_INTERVAL):
        return; # Too soon since last one sent.
    
    while True:
        time.sleep(2)
        try:
            temp = sensor.temperature
            #prev_temp = temp
            time.sleep(2)
            humid = sensor.humidity
            #prev_humid = humid
        except:
            print("An exception occurred")  
            continue  
        
        message_1, message_2 = weather_report(temp, humid)
        publish_message = message_1 + " / " + message_2
        
        if (prev_humid is None or prev_temp is None) or (temp != prev_temp and humid != prev_humid):
            prev_temp = temp
            prev_humid = humid
            display_message(message_1, message_2)
            
        print("Publishing: {0} to {1} ... ".format(temp, AIO_TEMP_FEED), end='')
        print("Publishing: {0} to {1} ... ".format(humid, AIO_HUMID_FEED), end='')
        print("Publishing: {0} to {1} ... ".format(publish_message, AIO_MESSAGE_FEED), end='')
        
        try:
            client.publish(topic=AIO_TEMP_FEED, msg=str(temp))
            client.publish(topic=AIO_HUMID_FEED, msg=str(humid))
            client.publish(topic=AIO_MESSAGE_FEED, msg=str(publish_message))
            print("DONE")
        except Exception as e:
            print("FAILED")
        finally:
            last_random_sent_ticks = time.ticks_ms()
            
def weather_report(temp, humidity):
    temperature = int(temp)
    message_1 = " "
    message_2 = " "
    if temperature > 30 and humidity < 70:
        message_1 = str(temperature)+"C Too hot!"
        message_2 = "Shorts & flops!"
    elif temperature > 25 and humidity < 70:
        message_1 = str(temperature)+"C Warm weather"
        message_2 = "T-shirt & hat"
    elif temperature > 20 and humidity < 70:
        message_1 = str(temperature)+"C Nice weather"
        message_2 = "Light jacket"
    elif temperature > 10 and humidity < 70:
        message_1 = str(temperature)+"C Bit chill"
        message_2 = "Jacket"
    elif temperature > 0 and humidity > 70:
        message_1 = str(temperature)+"C Rainy day"
        message_2 = "Rain cloths"
    elif temperature > 0 and humidity < 70:
        message_1 = str(temperature)+"C Too cold"
        message_2 = "Overalls"
    elif temperature < 0 and humidity > 70:
        message_1 = str(temperature)+"C Snow day"
        message_2 = "Put everything"
    else:
        message_1 = str(temperature)+"C Too cold"
        message_2 = "Overalls"
        
    display_message(message_1, message_2)
        
    return message_1, message_2
    
def display_message(message_1, message_2):
    I2C_ADDR = i2c.scan()[0]
    lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)
    print()
    lcd.move_to(0,0)
    lcd.putstr(message_1+"\n")
    lcd.move_to(0,1)
    lcd.putstr(message_2)

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


try:                      
    while 1:              # Repeat this loop forever
        client.check_msg()# Action a message if one is received. Non-blocking.
        get_temperature()
finally:                  # If an exception is thrown ...
    client.disconnect()   # ... disconnect the client and clean up.
    client = None
    print("Disconnected from Adafruit IO.")
    
# TO DO:
    """
    * Code part:
    
    - Send message from dashboard to the display for the weather condition
    - Separate methods out of the main()
    - Clean the code
    
    * Theory part 
    
    - Complete Quiz #3
    - Write report on GitHub
    
    """