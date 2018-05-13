#!/bin/bash
sudo cp /etc/dhcpcd.conf.adc /etc/dhcpcd.conf
sudo cp /etc/dnsmasq.conf.adc /etc/dnsmasq.conf
sudo cp /etc/default/hostapd.adc /etc/default/hostapd
sleep 5 
sudo shutdown -h 0
