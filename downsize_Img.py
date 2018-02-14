import base64
from PIL import Image

cam_pic = Image.open("test2.jpg")
print(cam_pic.size)
cam_pic = cam_pic.resize((640,480),Image.ANTIALIAS)
cam_pic.save("test2_scaled.jpg", quality=20)
