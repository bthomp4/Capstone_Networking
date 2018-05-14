#!/bin/bash

sudo rm -f /home/pi/different.txt
sudo diff -q /etc/dhcpcd.conf.adc /etc/dhcpcd.conf > /home/pi/different.txt
sudo diff -q /etc/dnsmasq.conf.adc /etc/dnsmasq.conf > /home/pi/different.txt
sudo diff -q /etc/default/hostapd.adc /etc/default/hostapd > /home/pi/different.txt
FILESIZE=$(stat -c%s "/home/pi/different.txt")
if [ $FILESIZE != 0 ]
then
    sudo cp /etc/dhcpcd.conf.adc /etc/dhcpcd.conf
    sudo cp /etc/dnsmasq.conf.adc /etc/dnsmasq.conf
    sudo cp /etc/default/hostapd.adc /etc/default/hostapd
    sleep 5 
    reboot
fi

