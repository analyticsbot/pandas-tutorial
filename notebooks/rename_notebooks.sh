#!/bin/bash
# Script to rename notebook files with leading zeros for better sorting

for file in part_*.ipynb; do
  # Extract the number part
  number=$(echo $file | sed 's/part_\([0-9]*\).ipynb/\1/')
  
  # Format with leading zeros (3 digits)
  formatted_number=$(printf "%03d" $number)
  
  # Create new filename
  new_file="part_${formatted_number}.ipynb"
  
  # Rename the file if it's different
  if [ "$file" != "$new_file" ]; then
    mv "$file" "$new_file"
    echo "Renamed $file to $new_file"
  fi
done
