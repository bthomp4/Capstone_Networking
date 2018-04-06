def encodeSensorData(rightSensor, leftSensor):
    dataString = ""
    dataString = dataString + str(rightSensor) + '!' + str(leftSensor)
    
    return dataString

def main():

    while true:

        rightSensorData = 78
        leftSensorData = 90

        dataString = encodeSensorData(rightSensorData, leftSensorData)

        # send data string

main()