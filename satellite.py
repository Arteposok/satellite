from machine import Pin, ADC, I2C
import time
import math
import uasyncio as asyncio
import network
import ujson
import usocket
from pico_i2c_lcd import I2cLcd

VREF = 3.3
ADC_MAX = 65535
BETA = 3950 
R0 = 10000
T0 = 298.15
R_FIXED = 10000
adc_thermistor = ADC(27)
adc_ldr = ADC(28)
working_diode = Pin(15, Pin.OUT)
working_diode.value(0)

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
I2C_ADDR = i2c.scan()[0]
lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

def read_voltage(adc):
    return (adc.read_u16() / ADC_MAX) * VREF

def read_light_level():
    v = read_voltage(adc_ldr)
    return (v / VREF) * 1000

async def connect():
    '''wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect("artem", "posokhov")
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)
    print("Connected:", wlan.ifconfig())
    return wlan.ifconfig()[0]'''
    ap = network.WLAN(network.AP_IF)
    ap.config(essid="Satellite", password="by_artem")  # optional password
    ap.active(True)
    return ap.ifconfig()[0]
    
async def run_socket():
    server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8888))
    server.listen()
    client, _ = server.accept()
    print("recieved a connection")
    return client, server

async def main():
    working_diode.value(0)
    lcd.clear()
    lcd.putstr("Connecting to wifi")
    ip = await connect()
    lcd.clear()
    lcd.putstr(f"'Satellite' {ip}")
    client, server = await run_socket()
    try:
        while True:
            lcd.clear()
            lcd.blink_cursor_on()
            working_diode.value(1)
            raw = adc_thermistor.read_u16()
            v = raw * 3.3 / 65535
            temp = 1.0 / ( math.log(v / 3.3) / 4300.0 + 1.0 / 298.0) - 273.0;
            light = read_light_level()
            
            print(f"Temperature: {temp} °C, Light: {light} lux (approx)")
            lcd.putstr(f"{temp} C; ~ {light} lux")
            
            client.send(ujson.dumps([temp, light]).encode())
            
            lcd.backlight_on()
            await asyncio.sleep(0.5)
    except:
        lcd.clear()
        lcd.putstr("Finished")
        working_diode.value(0)
    finally:
        lcd.clear()
        lcd.putstr("Finished")
        working_diode.value(0)
        server.close()
        client.close()
        
asyncio.run(main())
