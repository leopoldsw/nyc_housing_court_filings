#!/bin/bash

# Run Python script
python3 main.py

# Copy processed files to AWS folders

aws s3 cp data/uploads s3://files.osdcdata.com/social/nyc_hcf/ --recursive --include "*.csv" #--exclude "*.jpg"  
