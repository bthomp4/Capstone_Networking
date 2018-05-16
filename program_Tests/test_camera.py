from picamera import PiCamera
#from time import sleep

camera = PiCamera()

#camera.start_preview()

picture = ('test.jpg')

camera.capture(picture)
#camera.stop_preview()
