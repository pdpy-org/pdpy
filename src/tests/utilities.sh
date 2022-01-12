#!/bin/bash

CODEPATH=../pdpy
CODEBASE=$(find $CODEPATH -name "*.py")

function classes_and_methods {
  local file="$1"
  date > $file

  for i in $CODEBASE
  do
    n=$(cat $i | wc -l | tr -d ' ')
    echo $i "<---------[ $n lines ]" >> $file
    grep -n "^class" $i >> $file
    grep -n "def " $i >> $file
    echo === >> $file
  done
}
# get all the classes and method definitions into the given file
classes_and_methods "definitions.txt"