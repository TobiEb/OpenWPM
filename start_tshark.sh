#!/bin/sh

# $1 is url
# $2 is visit_id

/usr/bin/tshark -i eth0 -w /home/OpenWPM/Output/tshark/$1$2.pcap -q &
