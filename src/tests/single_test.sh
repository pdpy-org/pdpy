#!/bin/bash
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #

if [[ -f $1 ]] && [[ $2 ]]
then
  infile=$1
  outfile=$2
  fro=$(basename $infile | awk -F '.' '{ print $NF}')
  to=$(basename $outfile | awk -F '.' '{ print $NF}')
  echo translating $infile $outfile $to $fro
else
  echo "Usage: ./batch_test.sh input output"
fi

# The python script that performs the translation
file=$(pwd)/../translate.py

# The python3 executable
py=/usr/local/bin/python3

# The error log file
err=$(pwd)/error.log

# Place the pddb.json file in the INT variable
INT=$(pwd)/../../pddb/pddb.json

# clear the error log
echo Logfile created by single_test.sh on $(date) > $err

$py $file --int $INT -t $to -f $fro -i $infile -o $outfile >> $err 2>&1
