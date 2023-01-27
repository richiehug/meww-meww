import machine, neopixel
from time import sleep
from machine import Timer

leds = 24
ledRings = 2
PIXEL_NUMBER = leds * ledRings
timer = Timer(-1)
timerElapsed = False

ledStart = 0
ledFinish = 3
currentPixel = 0
currentLedRing = 0
offset = leds

np = neopixel.NeoPixel(machine.Pin(6), PIXEL_NUMBER)
red = (15, 0, 0)
black = (0, 0, 0)
np.fill(black)
np.write()

def rings():
    np[currentPixel + offset - 1] = black
    if currentPixel + offset < PIXEL_NUMBER:
        np[currentPixel + offset] = red
    else:
        np[0 + leds * (currentLedRing-1)] = red
    np.write()
    timer.init(period = 20, mode = Timer.ONE_SHOT, callback = changeLedValues)

def changeLedValues(timer):
    global currentPixel, offset
    
    if currentPixel < PIXEL_NUMBER:
        currentPixel += 1
    else:
        currentPixel = 0
        
        if currentLedRing < ledRings:
            offset += offset 
        else:
            offset = 0
        
    rings()
    
rings()
