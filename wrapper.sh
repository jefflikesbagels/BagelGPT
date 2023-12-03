#!/bin/bash

# Run main.py
python3 main.py

# Capture the return code of main.py
return_code=$?

# Check the return code
if [ $return_code -eq 1001 ]; then
    echo "main.py returned the expected code 1001. Performing additional actions..."
    # Perform additional actions here
else
    echo "main.py returned a different code ${return_code}. Exiting."
fi