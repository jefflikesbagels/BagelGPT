#!/bin/bash

# Run main.py
python3 main.py

# Capture the return code of main.py
return_code=$?

# Check the return code
if [ $return_code -eq 123 ]; then
    echo "main.py returned the expected code 123. Performing additional actions..."
    # Perform additional actions here
else
    echo "main.py returned a different code. Exiting."
fi