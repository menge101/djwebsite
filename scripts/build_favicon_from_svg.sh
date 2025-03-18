#!/usr/bin/env bash
# Primary purpose of this script is to retain the knowledge of how to build the favicon.
if [ -z "$1" ]
then
  echo "You must two arguments; first the path to the SVG source file"
  echo "Second you should specify an output file, default is icon.ico"
  exit
else
  sourcesvg=$1
fi
if [ -z "$2" ]
then
  output="icon.ico"
else
  output=$2
fi
echo "got to here"
inkscape -w 16 -h 16 -o 16.png "$sourcesvg"
inkscape -w 32 -h 32 -o 32.png "$sourcesvg"
inkscape -w 48 -h 48 -o 48.png "$sourcesvg"
magick 16.png 32.png 48.png "$output"