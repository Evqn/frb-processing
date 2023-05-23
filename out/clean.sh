#!/bin/bash

# List of directories
dirs=(cs dada fil vdr)

# Parent directory containing the folders
parent_dir="."

# Or alternatively:
# parent_dir=$(pwd)

# Loop over each directory
for dir in "${dirs[@]}"; do
    # Full path to the directory
    full_path="${parent_dir}/${dir}"

    # Check if the directory exists
    if [[ -d "${full_path}" ]]; then
        # Remove all files in the directory
        rm -f "${full_path}"/*
    else
        echo "Directory ${full_path} does not exist."
    fi
done
