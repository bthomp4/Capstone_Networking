import tkinter
from PIL import Image, ImageTk
#Source: https://bytes.com/topic/python/answers/933486-tkinter-reloading-window-displaying-image

def update_image():
    global camImg
    camImg = ImageTk.PhotoImage(Image.open("tempPic.jpg"))
    label.config(image = camImg)
    label.after(1000,update_image)
    print("Updated")

w = tkinter.Tk()
im = Image.open("tempPic.jpg")
camImg = ImageTk.PhotoImage(im)
label = tkinter.Label(w,image=camImg)
print("Loaded")
label.pack()
w.after(1000,update_image)
w.mainloop()
