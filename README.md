# Capstone_Networking

## Project Goal
The goal of this project is to connect two Raspberry Pi Zero Ws together using an ad hoc network

## Project Tasks
1. Create an ad hoc Network using one of the Raspberry Pi Zero Ws
   - This may be done using the command line or programming / scripting language
    - If done using the command line create a txt file that contains the commands used
2. Connect the second Raspberry Pi Zero W to the created ad hoc network
   - This may be done using the command line or programming / scripting language
    - If done using the command line create a txt file that contains the commands used
3. Use the created link to pass messages between the two Raspberry Pis
   - The messages should be sent using UDP packets 
   - This may be done using command line or programming /scripting language
4. If not previously done, complete 1-3 with a programming / scripting language
5. Use the connected ad hoc network to send an image taken with the camera on one pi to the display connected to the second pi
6. Use the connected ad hoc network to send sensor information from the ultrasonic sensors connected to one pi, to the display of the second pi
7. Join this program with into one with the other programs

## Additional Info
### Setting up Ad Hoc Network for Raspberry Pi
1. Install the required software
   ```
   sudo apt-get install dnsmasq hostapd
   ```
2. Since the configuration files are not ready yet, turn the software off
   ```
   sudo systemctl stop dnsmasq
   sudo systemctl stop hostapd
   ```
3. Configuring a static IP:
   3.1 Copy the current contents of the configuration file
      ```
      sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.wifi
      sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.adc
      ```
   3.2 Edit the dhcpcd.conf.adc file
      ```
      sudo vim /etc/dhcpcd.conf.adc
      ```
   3.3 Go to the end of file and add the following lines:
      ```
      interface wlan0
      static ip_address=192.168.4.1/24
      ```
   3.4 Now copy the contents of this file into dhcpcd.conf
      ```
      sudo cp /etc/dhcpcd.conf.adc /etc/dhcpcd.conf
      ```
   3.5 Now restart the dhcpcd daemon and set up the new wlan0 configuration.


## Project Links
https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md
