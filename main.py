import time
import network
from machine import Pin, ADC, I2C
from ssd1306 import SSD1306_I2C
import BlynkLib

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("riya", "riya0000")
BLYNK_AUTH = 'f4ZqGtcmCq5EvzZdb7fsVfG3T5sRi-xT'

wait = 10
while wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')

ip = wlan.ifconfig()[0]
print('IP: ', ip)

blynk = BlynkLib.Blynk(BLYNK_AUTH)
relay1_pin = Pin(15, Pin.OUT)
buzzer_pin = Pin(16, Pin.OUT)
sm_sensor = ADC(Pin(26))
min_moisture = 19200
max_moisture = 66000
readDelay = 2
WIDTH = 128
HEIGHT = 64
i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=400000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

@blynk.on("V1")
def v1_write_handler(value):
    if value and len(value) > 0:
        if int(value[0]) == 1:
            relay1_pin.value(1)
        else:
            relay1_pin.value(0)
    else:
        print("Invalid value received from Blynk")

buzzer_duration = 3
buzzer_triggered = False

while True:
    oled.fill(0)
    moisture = (max_moisture - sm_sensor.read_u16()) * 100 / (max_moisture - min_moisture)

    if moisture < 20:
        oled.text("Low Moisture", 10, 15)
    elif 21 <= moisture <= 65:
        oled.text("Normal Moisture", 10, 15)
    else:
        oled.text("High Moisture", 10, 15)

    print("moisture: " + "%.2f" % moisture + "% (adc: " + str(sm_sensor.read_u16()) + ")")
    oled.text(str("%.2f" % moisture)+" %", 35, 35)
    oled.show()
    blynk.virtual_write(0, moisture)

    if moisture < 20:
        relay1_pin.value(0)
    elif moisture > 65:
        relay1_pin.value(1)

    if moisture > 70 or moisture < 20:
        if not buzzer_triggered:
            buzzer_pin.value(1)
            time.sleep(buzzer_duration)
            buzzer_pin.value(0)
            buzzer_triggered = True
    else:
        buzzer_triggered = False
        buzzer_pin.value(0)

    blynk.run()
    time.sleep(readDelay)
