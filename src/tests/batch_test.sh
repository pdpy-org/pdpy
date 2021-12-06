#!/bin/bash
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #

if [[ $1 == 'help' ]] || [[ $1 == '-h' ]] || [[ $1 == '--help' ]]
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

# Place the pddb.json file in the INT variable
INT=$(pwd)/../internals/pddb.json

# If there is a second argument, it is the offset to start from
if [[ $2 ]]
then 
  offset=$2
else
  offset=0
fi

# clear the error log
echo Logfile created by batch_test.sh on $(date) > $err

# Make the output directory
mkdir -p $outdir

# store the number of lines
i=0

function translate_all
{
  # the commands to be executed
  # to translate files into all formats
  local input=$1
  local name=$(basename $input)
  # echo "Translating $input -- $name"
  json_out="$outdir/$name.json"
  pkl_out="$outdir/$name.pkl"
  xml_out="$outdir/$name.xml"
  json_ref="$outdir/$name"
  pkl_ref="$outdir/$name-pkl_ref.pd"
  xml_jref="$outdir/$name-xml_ref.json"
  xml_ref="$outdir/$name-xml_ref.pd"
  $py $file -int $INT -f 'pd'   -t 'json' -i $input    -o $json_out >> $err 2>&1
  if [[ ! -f $json_out ]]; then return; fi
  $py $file -int $INT -f 'pd'   -t 'pkl'  -i $input    -o $pkl_out  >> $err 2>&1
  if [[ ! -f $pkl_out ]]; then return; fi
  $py $file -int $INT -f 'json' -t 'pd'   -i $json_out -o $json_ref >> $err 2>&1
  if [[ ! -f $json_ref ]]; then return; fi
  $py $file -int $INT -f 'pkl'  -t 'pd'   -i $pkl_out  -o $pkl_ref  >> $err 2>&1
  if [[ ! -f $pkl_ref ]]; then return; fi
  $py $file -int $INT -f 'json' -t 'xml'  -i $json_out -o $xml_out  >> $err 2>&1
  if [[ ! -f $xml_out ]]; then return; fi
  $py $file -int $INT -f 'xml'  -t 'json' -i $xml_out  -o $xml_jref >> $err 2>&1
  if [[ ! -f $xml_jref ]]; then return; fi
  $py $file -int $INT -f 'json' -t 'pd'   -i $xml_jref -o $xml_ref  >> $err 2>&1
}

while read line; do
  echo $i "${line}"

  if [[ ! $3 ]]; then
    translate_all "${line}"
    if grep -q "ERROR" $err; then
      echo "Stopped at: " "${line}"
      echo "line number"
      echo $(grep -n "${line}" $1 | cut -f 1 -d:)
      break
    fi 
  else
    translate_all "${line}"
    break
  fi
  i=$((i+1))

done < <(tail -n +$offset $1)
