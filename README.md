# Capstone_Networking

## Project Goal
The goal of this project is to connect two Raspberry Pi Zero Ws together using an ad hoc network

## Project Tasks
1. ~Create an ad hoc Network using one of the Raspberry Pi Zero Ws~
   - ~This may be done using the command line or programming / scripting language~
    - ~If done using the command line create a txt file that contains the commands used~
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
### How to setup an Ad Hoc Network on Raspberry Pi
1. From the command line, go to the following directory
	```
	cd /etc/network
	```
2. Copy the existing interfaces file as a backup
	```
	sudo cp interfaces interfaces-wifi
	```
3. Create a new file for our ad-hoc network
	```
	sudo vim interfaces-adhoc
	```
4. Once file is open, copy the following into the file
	```
	auto lo
	iface lo inet loopback
	iface eth0 inet dhcp
	
	auto wlan0
	iface wlan0 inet static
	address 192.168.1.1
	netmask 255.255.255.0
	wireless-channel 1
	wireless-essid RPwireless
	wireless-mode ad-hoc
	```
5. Save the file
6. Install a package to allow the Pi to assign a device connecting to it an IP address.
	```
	sudo apt-get update
	sudo apt-get install isc-dhcp-server
	```
7. Step 6 created a config file that needs to be edited. Now open the file.
	```
	sudo vim /etc/dhcp/dhcpd.conf
	```
8. Edit the file to contain the following:
	```
	ddns-update-style interim;
	
	default-lease-time 600;
	
	max-lease-time 7200;
	
	authoritative;
	
	log-facility local7;
	
	subnet 192.168.1.0 netmask 255.255.255.0 {
	range 192.168.1.5 192.168.1.150;
	}
	```
9. Save the file and reboot the Pi.
10. Now in order to switch between the wifi interfaces and the ad-hoc interfaces do the following:

	If you want to use the ad-hoc network do the following:
	```
	cd /etc/network
	sudo cp interfaces-adhoc interfaces
	```

	Then reboot the Pi.

	If you want to use the wifi network, do the following:
	```
	cd /etc/network
	sudo cp interfaces-wifi interfaces
	```

	Then reboot the Pi.
