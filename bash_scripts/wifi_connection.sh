#!/bin/bash
sudo cp /etc/dhcpcd.conf.wifi /etc/dhcpcd.conf
sudo cp /etc/dnsmasq.conf.orig /etc/dnsmasq.conf
sudo cp /etc/default/hostapd.orig /etc/default/hostapd
sleep 2
reboot
