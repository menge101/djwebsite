#!/bin/bash

for file in ./requirements/*.txt; do
    if [ -f "$file" ]; then
      extension="${file##*.}"
      filename="${file%.*}"
      echo $extension
      echo $filename
      uv pip compile --no-header --quiet --generate-hashes -o $filename.lock $file
    fi
done
