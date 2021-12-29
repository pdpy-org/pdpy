#!/bin/bash
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #

# Test if the json and xml ref pd file differ


files=$(ls json_files/*.pd | awk '!/_ref/ {print $0}' )
for file in $files
do
    echo "Testing $file"
    echo "----------------------------------------"
    diff "$file" "$file-xml_ref.pd"
done