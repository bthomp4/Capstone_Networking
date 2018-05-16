# Capstone_Networking

## Project Goal
The goal of this project is to connect two Raspberry Pi Zero Ws together using an ad hoc network

## Project Tasks
~1. Create an ad hoc Network using one of the Raspberry Pi Zero Ws~
   - ~This may be done using the command line or programming / scripting language~
    - ~If done using the command line create a txt file that contains the commands used~
~2. Connect the second Raspberry Pi Zero W to the created ad hoc network~
   - ~This may be done using the command line or programming / scripting language~
    - ~If done using the command line create a txt file that contains the commands used~
~3. Use the created link to pass messages between the two Raspberry Pis~
   - ~The messages should be sent using UDP packets~
   - ~This may be done using command line or programming /scripting language~
~4. If not previously done, complete 1-3 with a programming / scripting language~
~5. Use the connected ad hoc network to send an image taken with the camera on one pi to the display connected to the second pi~
~6. Use the connected ad hoc network to send sensor information from the ultrasonic sensors connected to one pi, to the display of the second pi~
~7. Join this program with into one with the other programs~

## Additional Tasks:
~1. Figure out how to change Image to a string, and then from string back to Image~
~2. Create a socket program to send image from server to client~

   ~2.1 Figure out how to compress an image using python~
   
      ~2.1.1 Try compressing the image after taking the picture~
    
3. Create bash scripts for running the socket program on server and client side

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
      ```
      sudo systemctl restart dhcpcd
      ```
4. Configuring the DHCP server (dnsmasq)
   
   4.1 Rename the configuration file and edit a new one:
      ```
      sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
      sudo vim /etc/dnsmasq.conf
      ```
   4.2 Add the following info into the dnsmasq configuration file and save:
      ```
      interface=wlan0
      dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
      ```
5. Configuring the access point host software (hostapd)
   
   5.1 Edit the hostapd config file to add parameters for wireless network
      ```
      sudo vim /etc/hostapd/hostapd.conf
      ```
   5.2 Add the following information to the configuration file:
      ```
      interface=wlan0
      driver=nl80211
      ssid=RPiWireless
      hw_mode=g
      channel=7
      wmm_enabled=1
      macaddr_acl=0
      auth_algs=1
      ignore_broadcast_ssid=0
      wpa=2
      wpa_passphrase=raspberry
      wpa_key_mgmt=WPA-PSK
      wpa_pairwise=TKIP
      rsn_pairwise=CCMP
      ```
   5.3 Now we need to tell the system where to find the config file from 5.2
      ```
      sudo vim /etc/default/hostapd
      ```
   5.4 Find the line with #DAEMON_CONF, and replace it with the following:
      ```
      DAEMON_CONF="/etc/hostapd/hostapd.conf"
      ```
6. Start it up
   
   6.1 Now start up the remaining services
      ```
      sudo systemctl start hostapd
      sudo systemctl start dnsmasq
      ```
7. Now Reboot and should be good to go!
8. In order to change back and forth between wifi and ad-hoc network:
   
   8.1 To change back to wifi:
      ```
      sudo cp /etc/dhcpcd.conf.wifi /etc/dhcpcd.conf
      ```
   
   8.1.1 Then Reboot the Pi
   
   8.2 To change back to ad-hoc:
      ```
      sudo cp /etc/dhcpcd.conf.adc /etc/dhcpcd.conf
      ```
## Project Links/ Helpful Tips
### For Access Point References
https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md

https://frillip.com/using-your-raspberry-pi-3-as-a-wifi-access-point-with-hostapd/
### For Socket Programming/ Image Transferring References

http://effbot.org/imagingbook/image.htm

### Special Note: Focus on using something that takes the image and puts it into a string

https://raspberrypi.stackexchange.com/questions/67328/send-image-from-one-raspberry-pi-to-another-via-socket

### For encoding and decoding images in python

https://code.tutsplus.com/tutorials/base64-encoding-and-decoding-using-python--cms-25588

## For compressing images using PIL in python

https://stackoverflow.com/questions/10607468/how-to-reduce-the-image-file-size-using-pil

## For Running bash script at startup:

   1. Edit the rc.local file 
      ```
      sudo vim /etc/rc.local
      ```
   2. Add in the bash script that you wish to run
      ```
      sudo /home/pi/Capstone_Networking/bash_scripts/./startup.sh
      ```

