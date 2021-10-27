#!/bin/bash
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #

if [[ $1 -eq 'help' ]] || [[ $1 -eq '-h' ]] || [[ $1 -eq '--help' ]]
then
  echo "Usage: ./batch_test.sh pathfile [offset, once]"
  echo """Options:
Argument 1: pathfile
 -  A file containing the list of pure data file paths to be translated
Argument 2 (optional): offset
 - the offset into the file to start the translation from
Argument 3 (optional): once
 - If present, do only the current file and stop
 - If not present, do all the files in the list and stop on Error
"""
  echo "./batch_test.sh help (shows this help message and exits)"
  exit
fi

# The python script that performs the translation
file=$(pwd)/../translate.py

# The python3 executable
py=/usr/local/bin/python3

# The output directory
outdir=$(pwd)/json_files

# The error log file
err=$(pwd)/error.log

# If there is a second argument, it is the offset to start from
if [[ $2 ]]
then 
  offset=$2
else
  offset=0
fi

# clear the error log
echo > $err

# Make the output directory
mkdir -p $outdir

# store the number of lines
i=0

while read line; do
  echo $i "$line"
  input="$line"
  out="$outdir/$(basename $line).json"
  out1="$outdir/$(basename $line).pkl"
  out2="$outdir/$(basename $line)-ref.pd"
  out3="$outdir/$(basename $line)-ref2.pd"

  # the commands to be executed
  # to translate files into all formats

  if [[ ! $3 ]]; then
    $py $file -f 'pd'   -t 'json' -i "$input" -o "$out"  >> $err 2>&1
    $py $file -f 'pd'   -t 'pkl'  -i "$input" -o "$out1" >> $err 2>&1
    $py $file -f 'json' -t 'pd'   -i "$out"   -o "$out2" >> $err 2>&1
    $py $file -f 'pkl'  -t 'pd'   -i "$out1"  -o "$out3" >> $err 2>&1
    if grep -q "Error" $err; then
      echo "Stopped at: " $input
      echo "line number"
      echo $(grep -n $input $1 | cut -f 1 -d:)
      break
    fi 
  else
    $py $file -f 'pd'   -t 'json' -i "$input" -o "$out"  >> $err 2>&1
    $py $file -f 'pd'   -t 'pkl'  -i "$input" -o "$out1" >> $err 2>&1
    $py $file -f 'json' -t 'pd'   -i "$out"   -o "$out2" >> $err 2>&1
    $py $file -f 'pkl'  -t 'pd'   -i "$out1"  -o "$out3" >> $err 2>&1
    break
  fi
  i=$((i+1))

done < <(tail -n +$offset $1)
