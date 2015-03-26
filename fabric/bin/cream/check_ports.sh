#!/bin/bash

for port in 8443 2811 49152 49155 49154 9002 9001 3306 2170 33333 56565; do
    nc -z -w5 localhost $port
done
