#!/bin/bash

n=0
for file in /run/media/Documents/pcaps/torclient*-127.0.0.1.pcap;do
  tshark -n -t e -r $file "tcp.flags == 0x002" | tail +3 | awk 'NR%2==1' | awk '{print $2}' > $file.log
  n=$((n+1))
done

n=0
for file in /run/media/Documents/pcaps/fileserver*-11.0.*pcap;do
  tshark -n -t e -r $file "tcp.flags == 0x012" | awk '{print $2}' > $file.log
  n=$((n+1))
done
