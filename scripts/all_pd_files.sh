#!/bin/bash
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #

# This script finds pure data patches and brings their paths 
# into separate files first. Then, it sorts them and removes dupes,
# and places them into one big text file.

# The root path where pdpy and pure-data are presumed to be located
ROOT=Documents

USER=$(whoami)

FULL_ROOT_PATH=/home/$USER/$ROOT

# All the patches root folders go here (stemming from $FULL_ROOT_PATH)
FILES=(pdpy-org/pdpy/tests/pd_files  pure-data/doc Pd)

# The output path
OUT=$FULL_ROOT_PATH/pdpy-org/pdpy/tests/patch_paths

# the python executable
PY=python

# place the remove_dupes.py script in a variable
REM_DUPES=$FULL_ROOT_PATH/pdpy-org/pdpy/scripts/remove_dupes.py

function finder {
  # This function finds all the patches in the given folder
  # and places their paths into separate files.
  local path="$1"
  local name=$OUT/individual/$(basename $path).txt
  if [[ -d $path ]]; then
    echo "$path -> $name"
    find $path -name "*.pd" -type f | awk '{gsub(" ","\\ ",$0);print $0}' > $name
    cat $name >> /tmp/allfiles
  else
    echo "No such path: $path"
  fi

}

touch /tmp/allfiles
mkdir -p $OUT
mkdir -p $OUT/individual

# Run the finder function for each of the folders
for file in ${FILES[@]}
do
  finder $FULL_ROOT_PATH/$file
done

# execute the remove_dupes.py script 
# with input /tmp/allfiles and output to $OUT/all_files.txt
$PY $REM_DUPES -i /tmp/allfiles -o $OUT/all_files.txt

# Remove the temporary file
rm /tmp/allfiles
