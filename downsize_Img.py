import base64
from PIL import Image

dog_image = Image.open("dog1.jpg")
print(dog_image.size)
dog_image = dog_image.resize((800,480),Image.ANTIALIAS)
dog_image.save("dog1_scaled.jpg", quality=20)
