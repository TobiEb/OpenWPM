#!/bin/sh

# $1 is url
# $2 is visit_id

/usr/bin/tshark -i wlp3s0 -w /home/tobi/Workspace/OpenWPM/Output/tshark/$1$2.pcap -q &