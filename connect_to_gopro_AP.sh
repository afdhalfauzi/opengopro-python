#!/bin/bash
ssid=GoProHero9Angkasa
password=NPc-hg6-S5S 

echo "Connecting to GoPro AP..."
sudo nmcli dev wifi connect "$ssid" password "$password"
echo "Connected"