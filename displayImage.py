import tkinter
from PIL import Image, ImageTk
#Source: https://bytes.com/topic/python/answers/933486-tkinter-reloading-window-displaying-image

from time import sleep

#from test_server import picture

picture = "tempPic.jpg"

def update_image():
    global camImg
    camImg = ImageTk.PhotoImage(Image.open(picture))
    label.config(image = camImg)
    #label.after(1000,update_image)
    print("Updated")

w = tkinter.Tk()
im = Image.open(picture)
camImg = ImageTk.PhotoImage(im)
label = tkinter.Label(w,image=camImg)
print("Loaded")
label.pack()
#w.after(1000,update_image)
#w.mainloop()
while True:
    sleep(1)
    w.after(0,update_image)
    #w.mainloop()
    w.update()
    w.update_idletasks()
