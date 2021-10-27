#!/bin/bash
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (c) 2021 Fede Camara Halac
# **************************************************************************** #

# This file contains the functions to manage the pddb database
# it is meant to be used with the get_internals.py script
# as well as the pdpy.py script

# The path to your pure data distribution
PD_PATH="/Users/fd/Development/pure-data"

# The path to the get_internals file
GET_INTERNALS="./get_internals.py"

# The path to the pddb python script
PDDB="./pddb.py"

# The path to python3
PY="/usr/local/bin/python3"

# The path to the pddb database
PDDB_FILE="./pddb.json"

# Check if the Pure Data path is valid
if [[ ! -d $PD_PATH ]]; then
  echo "Pure data path is not valid:" $PD_PATH
  exit
fi

touch /tmp/inter
touch /tmp/internals
touch /tmp/args

# Get the internals of the Pure Data distribution
for i in $(find $PD_PATH -type f -name "*.c")
do 
  grep "class_new" $i | grep gensym - | cut -f 2 -d\" | sed '/^ /d' >> /tmp/inter
  num=$(grep -n class_new $i | sed '/^ /d' | cut -f 1 -d:)
  echo $i: $num >> /tmp/args
done 

# Find the internals from the help-intro file as well
cat "$PD_PATH/doc/5.reference/help-intro.pd" |
grep "#X obj" - | cut -f 5 -d' ' | sed 's/;//' >> /tmp/inter

# Sort the internals and filter out the unique
sort /tmp/inter | uniq | sed '/^ /d' > /tmp/internals

# Remove the temporary internals file
rm /tmp/inter

# Try to run the get_internals script with the temp internals file
if [[ ! -f $GET_INTERNALS ]]; then
  echo "./get_internals.py is not present in current dir"
else
  echo "Running $GET_INTERNALS"
  $PY $GET_INTERNALS /tmp/internals /tmp/internals.json
  rm /tmp/internals
fi

# Try to run the pddb script with the temp internals and args files
if [[ ! -f $PDDB ]]; then
  echo "./pddb.py is not present in current dir"
else
  echo "Running $PDDB"
  $PY $PDDB /tmp/args /tmp/internals.json $PDDB_FILE
  rm /tmp/args 
  rm /tmp/internals.json
fi
