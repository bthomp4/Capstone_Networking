import base64
from PIL import Image

image = open('test4.jpg','rb')
image_read = image.read()
image_64_encode = base64.encodestring(image_read)

i = 0

for c in image_64_encode:
    i = i + 1	

print("Printing the encoded string")
print(image_64_encode)

image_64_decode = base64.decodestring(image_64_encode)
image_result = open('test4_decode.jpg','wb')
image_result.write(image_64_decode)

print("Opening the decoded image")
im = Image.open("test4_decode.jpg")
im.show()

print("Number of Characters:",i)
