def decodeSensorData(dataString):
    dataString = dataString.split('!')
    rightSensorData = int(dataString[0])
    leftSensorData = int(dataString[1])

    return rightSensorData,leftSensorData

def main():

    while True:

        dataString = "498!3849"

        rightSensorData,leftSensorData = decodeSensorData(dataString)

        print(rightSensorData)
        print(leftSensorData)

main()
