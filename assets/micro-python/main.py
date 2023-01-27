import i2c_lcd, neopixel

from machine import I2C, Timer, Pin, PWM
from Button import Button
from time import sleep, time
from random import randint, choice
from servo import Servo
import gc

# Globals
timer = timerA = timerB = timerC = timerD = Timer(-1)
buttonAActive = buttonBActive = buttonCActive = buttonDActive = True
buttonPauseDelay = 100
scene = 0
subScene = 0
restart = True
changeComponent = False

## Options
delay = 0           # delay
delayLimit = 16
repetitions = 1     # repetitions
repetitionsLimit = 9
interval = 0        # interval
intervalLimit = 16
timeUnit = 15       # 15min block

currentRepetition = 0
delayLeft = 0
intervalLeft = 0

## Screen
i2c_bus = I2C(0)
display = i2c_lcd.Display(i2c_bus, 0x3e)
display.color(255,255,255)

## LED Values
ledRing = 0
ledRings = 5
offset = 24
ledLength = 24 * ledRings
leds = neopixel.NeoPixel(machine.Pin(21), ledLength)
red = (255, 0, 0)
black = (0, 0, 0)
ledCount = 0
subSceneDelay = 4000

## Servo
SERVO_PIN_NUMBER = 17
servo_pin = PWM(Pin(SERVO_PIN_NUMBER))
servo_motor = Servo(servo_pin)

## Game
startGame = True
gameOngoing = True
initialRound = True
rotationCount = 0
rotationLimit = 20
touchSensor = 0
touchSensorActive = True
touchSensorPressed = False
score = 0
addScore = False
maxScore = 5
scoreLimit = 10
treatDelay = 250

# Console start new line
print('')

# Scene Handler
def changeScene(newScene):
    global scene, maxSubScenes, timer, startGame, gameOngoing

    display.home()
    display.clear()

    if newScene == 0:
        if restart: 
            reset()

        if subScene == 0:
            display.write('/|_/|  MEWW')
            display.move(0,1)
            display.write(' o.o     MEWW')

        elif subScene == 1:
            display.write('/|_/|  PRESS')
            display.move(0,1)
            display.write(' ^.^     [OK]')

        maxSubScenes = 1
        subSceneTimer = Timer(-1)
        subSceneTimer.init(period = subSceneDelay, mode = Timer.ONE_SHOT, callback = changeSubScene)

        
    elif newScene == 1:
        display.write('SET DELAY')
        display.move(0,1)
        h = int((delay * timeUnit - ((delay * timeUnit) % 60)) / 60)
        m = '%02d' % ((delay * timeUnit) % 60)
        display.write(f'[{h}h{m}min]')

    elif newScene == 2:
        display.write('SET REPETITIONS')
        display.move(0,1)
        display.write(f'[{repetitions}] times')

    elif newScene == 3:
        display.write('SET INTERVAL')
        display.move(0,1)

        h = int((interval * timeUnit - ((interval * timeUnit) % 60)) / 60)
        m = '%02d' % ((interval * timeUnit) % 60)
        display.write(f'[{h}h{m}min]')

    elif newScene == 4:
        if subScene == 0:
            display.write('READY TO START?')
            display.move(0,1)
            display.write(f'Press [OK]')
        if subScene == 1:
            display.write('READY TO START?')
            display.move(0,1)

            hd = int((delay * timeUnit - ((delay * timeUnit) % 60)) / 60)
            md = '%02d' % ((delay * timeUnit) % 60)
            hi = int((interval * timeUnit - ((interval * timeUnit) % 60)) / 60)
            mi = '%02d' % ((interval * timeUnit) % 60)

            display.write(f'D{hd}:{md} R{repetitions} I{hi}:{mi}')
        
        maxSubScenes = 1
        scene1Timer = Timer(-1)
        scene1Timer.init(period = subSceneDelay, mode = Timer.ONE_SHOT, callback = changeSubScene)


    elif newScene == 5:
        gameOngoing = True
        if subScene == 0:
            display.write('GAME RUNNING ^_^')
            display.move(0,1)
            display.write(f'[X] Cancel game')
        elif subScene == 1:
            hd = int((delay * timeUnit - ((delay * timeUnit) % 60)) / 60)
            md = '%02d' % ((delay * timeUnit) % 60)

            hi = int((interval * timeUnit - ((interval * timeUnit) % 60)) / 60)
            mi = '%02d' % ((interval * timeUnit) % 60)

            display.write('GAME RUNNING ^_^')
            display.move(0,1)
            display.write(f'D{hd}:{md} R{currentRepetition}/{repetitions} I{hi}:{mi}')
        
        maxSubScenes = 1
        scene5Timer = Timer(-1)
        scene5Timer.init(period = subSceneDelay, mode = Timer.ONE_SHOT, callback = changeSubScene)


    elif newScene == 6:
        if repetitions > 1:
            display.write(f'CAT WON {repetitions} TIMES!')
        else:
            display.write(f'CAT WON {repetitions} TIME!')
        display.move(0,1)
        display.write('[OK] Restart')

    scene = newScene

def changeSubScene(timer):
    global subScene

    if subScene < maxSubScenes:
        subScene += 1
    else:
        subScene = 0
    
    timer.deinit()

    changeScene(scene)

# Unblock Buttons
def activateButtonA(timer):
    global buttonAActive
    buttonAActive = True
    timer.deinit()

def activateButtonB(timer):
    global buttonBActive
    buttonBActive = True
    timer.deinit()

def activateButtonC(timer):
    global buttonCActive
    buttonCActive = True

def activateButtonD(timer):
    global buttonDActive
    buttonDActive = True
    timer.deinit()

def activateTouchSensor(timer):
    global touchSensorActive
    touchSensorActive = True
    timer.deinit()

def reset():
    # Reset program
    global score, addScore, timer, restart, subScene, delay, repetitions, interval, ledRing, touchSensor, currentRepetition
    global buttonAActive, buttonBActive, buttonCActive, buttonDActive
    global touchSensorActive
    global startGame, gameOngoing, initialRound, rotationCount

    buttonAActive = buttonBActive = buttonCActive = buttonDActive = True
    restart = False
    subScene = 0

    delay = 0
    score = 0
    addScore = False
    repetitions = 1
    currentRepetition = 0
    interval = 0

    ledRing = 0
    touchSensor = 0
    touchSensorActive = True
    startGame = True
    gameOngoing = False
    initialRound = True
    rotationCount = 0

    motorReturnHome()
    gc.collect()

# Button A Logic - Plus Button
def buttonAPressed(pin, event):
    global delay, repetitions, interval, buttonAActive

    if event == Button.PRESSED and buttonAActive:

        if scene == 1 and delay < delayLimit:
            delay += 1
            changeScene(scene)
        
        elif scene == 2 and repetitions < repetitionsLimit:
            repetitions += 1
            changeScene(scene)

        elif scene == 3 and interval < intervalLimit:
            interval += 1
            changeScene(scene)

        buttonAActive = False
        timerA.init(period = buttonPauseDelay, mode = Timer.ONE_SHOT, callback = activateButtonA)

            
# Button B Logic - Minus Button
def buttonBPressed(pin, event):
    global delay, repetitions, interval, buttonBActive
    
    if event == Button.PRESSED and buttonBActive:
        if scene == 1 and delay > 0:
            delay -= 1
            changeScene(scene)
        
        elif scene == 2 and repetitions > 1:
            repetitions -= 1
            changeScene(scene)

        elif scene == 3 and interval > 0:
            interval -= 1
            changeScene(scene)
    
    buttonBActive = False
    timerB.init(period = buttonPauseDelay, mode = Timer.ONE_SHOT, callback = activateButtonB)

# Button C Logic
def buttonCPressed(pin, event):
    global buttonCActive, restart, subScene, gameOngoing

    if event == Button.PRESSED and buttonCActive:

        if scene == 0:
            changeScene(1)
        elif scene == 1:
            changeScene(2)
        elif scene == 2:
            if repetitions > 1:
                changeScene(3)
            else:
                changeScene(4)
        elif scene == 3:
            changeScene(4)
        elif scene == 4:
            subScene = 0
            gameOngoing = True
            if startGame:
                initGame()
            changeScene(5)
        elif scene == 6:
            restart = True
            changeScene(0)

    buttonCActive = False
    timerC.init(period = buttonPauseDelay, mode = Timer.ONE_SHOT, callback = activateButtonC)

# Button D Logic
def buttonDPressed(pin, event):
    global buttonDActive, restart, gameOngoing

    if event == Button.PRESSED and buttonDActive:
        if scene == 1:
            changeScene(0)
        elif scene == 2:
            changeScene(1)
        elif scene == 3:
            changeScene(2)
        elif scene == 4:
            changeScene(3)
        elif scene == 5:
            gameOngoing = False
            restart = True
            changeScene(0)

    buttonDActive = False
    timerD.init(period = buttonPauseDelay, mode = Timer.ONE_SHOT, callback = activateButtonD)

# Touch Sensor Logic
def touchSensorPressed(pin, event):
    global touchSensorActive

    if event == Button.PRESSED and scene == 5 and touchSensorActive:
        sensorTouched()
        touchSensorActive = False 
        touchSensorTimer = Timer(-1)
        touchSensorTimer.init(period = 200, mode = Timer.ONE_SHOT, callback = activateTouchSensor)


def ledTurnOn(id):
    leds[id] = red
    leds.write()

def ledTurnOff(id):
    leds[id] = black
    leds.write()

def ledRingRotate(id):
    global score, addScore

    for i in range(id*offset, 24+id*offset):
        ledTurnOn(i)
        sleep(0.02)
        ledTurnOff(i)
        touchSensors[id].update()
        buttonD.update()
        if gameOngoing == False or addScore == True: break

    if gameOngoing:
        if addScore:
            increaseScore()

        if score < maxScore:
            newRepetitionTimer = Timer(-1)
            newRepetitionTimer.init(period = 10, mode = Timer.ONE_SHOT, callback = newRepetition)
        else:
            giveTreat()
            if currentRepetition < repetitions:
                awaitNewRoundTimer = Timer(-1)
                awaitNewRoundTimer.init(period = treatDelay, mode = Timer.ONE_SHOT, callback = awaitNewRound)
            else:
                print('Game over!')
                gameOngoing == False
                changeScene(6)

def initGame():
    global startGame

    startGame = False
    gameDelay(delay)

def gameDelay(delay):
    print(f'Starting delay of {delay*timeUnit} mins...')
    gameDelayTimer = Timer(-1)
    gameDelayTimer.init(period = 1000*60*delay*timeUnit+6000, mode = Timer.ONE_SHOT, callback = awaitNewRound)

def awaitNewRound(timer):
    newRoundDelay = Timer(-1)
    intervalDelay = Timer(-1)
    if currentRepetition == 0:
        giveTreat()
        newRoundDelay.init(period = treatDelay, mode = Timer.ONE_SHOT, callback = newRound)
    elif interval > 0:
        print(f'Starting interval of {interval*timeUnit} mins...')
        intervalDelay.init(period = 1000*60*interval*timeUnit, mode = Timer.ONE_SHOT, callback = awaitTreat)
    else:
        newRoundDelay.init(period = treatDelay, mode = Timer.ONE_SHOT, callback = newRound)
    timer.deinit()

def awaitTreat(timer):
    awaitTreatDelay = Timer(-1)
    giveTreat()
    awaitTreatDelay.init(period = treatDelay, mode = Timer.ONE_SHOT, callback = newRound)
    timer.deinit()

def newRound(timer):
    global score, startGame, currentRepetition

    score = 0
    currentRepetition += 1
     
    if startGame:
        print('Game started...')
        startGame = False

    print(f'Starting round: {currentRepetition}')
    getNewLedRing()
    ledRingRotate(ledRing)
    timer.deinit()

def newRepetition(timer):
    global rotationCount, addScore

    if rotationCount >= rotationLimit or addScore:
        getNewLedRing()
    else:
        rotationCount += 1
    
    if addScore:
        addScore = False
        rotationCount = 0
        
    ledRingRotate(ledRing)
    timer.deinit()

def getNewLedRing():
    global ledRing, rotationCount
    rotationCount = 0
    availableLedRings = [i for i in range(ledRings)]
    availableLedRings.remove(ledRing)
    ledRing = choice(availableLedRings)
    print(f'Changing led ring to {ledRing}')

def increaseScore():
    global score

    score += 1
    print(f'Old score: {score-1}')
    print(f'New score: {score}')

def sensorTouched():
    global addScore
    addScore = True
    print('Sensor touched')

def giveTreat():
    print('Giving treat to cat...')
    servo_motor.goto(240)
    motorTimer = Timer(-1)
    motorTimer.init(period = treatDelay, mode = Timer.ONE_SHOT, callback = resetMotor)

def resetMotor(timer):
    motorReturnHome()
    timer.deinit()

def motorReturnHome():
    servo_motor.goto(0)

buttonA = Button(26, rest_state = True, callback = buttonAPressed)
buttonB = Button(27, rest_state = True, callback = buttonBPressed)
buttonC = Button(28, rest_state = True, callback = buttonCPressed)
buttonD = Button(29, rest_state = True, callback = buttonDPressed)

touchSensor0 = Button(4, rest_state = False, callback = touchSensorPressed)
touchSensor1 = Button(7, rest_state = False, callback = touchSensorPressed)
touchSensor2 = Button(5, rest_state = False, callback = touchSensorPressed)
touchSensor3 = Button(19, rest_state = False, callback = touchSensorPressed)
touchSensor4 = Button(16, rest_state = False, callback = touchSensorPressed)

touchSensors = [touchSensor0, touchSensor1, touchSensor2, touchSensor3, touchSensor4]

changeScene(scene)

# Main program
while(True):

    if scene == 0:
        buttonC.update()

    elif scene == 1:
        buttonA.update()
        buttonB.update()
        buttonC.update()
        buttonD.update()
    
    elif scene == 2:
        buttonA.update()
        buttonB.update()
        buttonC.update()
        buttonD.update()
    
    elif scene == 3:
        buttonA.update()
        buttonB.update()
        buttonC.update()
        buttonD.update()
    
    elif scene == 4:
        buttonC.update()
        buttonD.update()
    
    elif scene == 5:
        buttonD.update()

    elif scene == 6:
        buttonC.update()
