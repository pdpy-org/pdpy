#!/bin/bash

CODEPATH=../pdpy
CODEBASE=$(find $CODEPATH -name "*.py")

function line_count {
  local num=$1
  if [[ $1 -le 0 ]]; then num=1000; fi
  for i in $CODEBASE
  do
    wc -l $i
  done | sort | tail -n $num
}

function classes_and_methods {
  local file="$1"
  date > $file
  # touch /tmp/temp
  for i in $CODEBASE
  do
    n=$(cat $i | wc -l | tr -d ' ')
    echo $i "<---------[ $n lines ]" >> $file
    grep -n "^class" $i >> $file
    # grep "^class" $i | awk '{printf "%s pass\n",$0}' >> /tmp/temp
    grep -n "def " $i >> $file
    echo === >> $file
  done
  # sort /tmp/temp > $file
  # rm /tmp/temp
}

# get all the classes and method definitions into the given file
# classes_and_methods "definitions.txt"
line_count $1