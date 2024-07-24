#!/bin/bash

# Start bluetoothctl command
bluetoothctl << EOF > output.txt
paired-devices
EOF

# Check the output
if grep -q "GoPro" output.txt; then
    echo "Bluetooth device is connected."
else
    echo "No Bluetooth device is connected."
fi

# Clean up
rm output.txt
