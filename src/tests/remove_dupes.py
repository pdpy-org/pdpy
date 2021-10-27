#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #

# This script is called by all_pd_files.sh to remove duplicated files

""" Remove duplicates file path entries if they have the same file name """

# load the argument parser and accept an input and output file paths
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='input file path', required=True)
parser.add_argument('-o', '--output', help='output file path', required=True)
args = parser.parse_args()

# exit if neither input nor output file paths are provided
if not args.input or not args.output:
    print('Please provide input and output file paths')
    exit()

# load the input file path
with open(args.input, 'r') as f:
  lines = f.readlines()

# split the file names in lines variable and store the file name in a list
file_names = []
all_files = []
for line in lines:
  file_name = line.split('/')[-1].strip()
  if file_name not in file_names:
    file_names.append(file_name)
    all_files.append(line)

# write the output file with the content of all_files variable
with open(args.output, 'w') as f:
  f.writelines(all_files)
