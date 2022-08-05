#!/bin/bash
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #

SHOW_DIFF=1

if [[ ! $1 ]] || [[ $1 == 'help' ]] || [[ $1 == '-h' ]] || [[ $1 == '--help' ]]
then
  echo "Usage: ./batch_test.sh [help | PATH] [FROM, ONCE]"
  printf "\t%s\t%s\n" "PATH" "A path to a text file containing the list of pure data file paths to be translated, eg: find . -name '*.pd' > myfile.txt"
  printf "\t%s\t%s\n" "help" "Print this help"
  echo "Argument 2 (optional):"
  printf "\t%s\t%s\n" "FROM" "the file line number from which to start the translation"
  echo "Argument 3 (optional):"
  printf "\t%s\t%s\n" "ONCE" "Translate only one file and stop, otherwise stop on ERROR"
  exit
fi

# The python script that performs the translation
file=$(pwd)/../scripts/translate.py

# The python3 executable
py=/usr/local/bin/python3

# The output directory
outdir=$(pwd)/output

# The error log file
err=$(pwd)/error.log

# Place the pddb.json file in the INT variable
INT=$(pwd)/../../pddb/pddb.json

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
  $py $file -int $INT -f 'xml'  -t 'pd' -i $xml_out  -o $xml_ref >> $err 2>&1
  if [[ ! -f $xml_ref ]]; then return; fi
  $py $file -int $INT -f 'xml' -t 'json'   -i $xml_out -o $xml_jref  >> $err 2>&1
  if [[ $SHOW_DIFF ]]; then diff $json_ref $xml_ref; fi
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
