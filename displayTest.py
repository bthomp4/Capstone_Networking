import tkinter as tk
from PIL import Image, ImageTk
import time

class SampleApp(tk.Tk):
    def __init__(self,*args,**kwargs):
        tk.Tk.__init__(self,*args,**kargs)
        self.root = tk.Frame()
        self.root.pack()

        self.update_image()

    def update_image(self):
        im = Image.open("dog.jpg")
        photo = ImageTk.PhotoImage(im)
        label = tk.Label(self.root,image=photo)
        label.photo = photo
        label.pack()
        self.after(5000,self.update_image)

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
