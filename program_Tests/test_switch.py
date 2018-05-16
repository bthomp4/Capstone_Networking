import RPi.GPIO as GPIO

GPIO_modeSel = 16
GPIO_LED     = 21

GPIO.setmode(GPIO.BCM)

GPIO.setup(GPIO_modeSel,GPIO.IN)
GPIO.setup(GPIO_LED,GPIO.OUT)

GPIO.output(GPIO_LED, False)

Flag = False
prev = False
while True:
    try:

        if GPIO.input(GPIO_modeSel) and Flag:
            print("In full battery mode")
            GPIO.output(GPIO_LED, True)
            Flag = False
        elif not GPIO.input(GPIO_modeSel) and Flag:
            print("In battery saver mode")
            GPIO.output(GPIO_LED, False)
            Flag = False
        else:
            curr = GPIO.input(GPIO_modeSel)
            if prev != curr:
                Flag = True
            prev = curr
            
    except KeyboardInterrupt:

        GPIO.cleanup()
