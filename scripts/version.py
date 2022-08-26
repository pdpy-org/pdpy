#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
# Bumps up the last version, for automated uploads 

def get_version(filename='pyproject.toml', 
                version_prefix="version ="):  

  version_line=0 # location of "version =" line in project file

  old_version='' # the old version in the project file

  prev_file = [] # store the entire project file

  # read the project file
  with open(filename) as f:
    for i, line in enumerate(f.readlines()):
      # check against "version = " to see if we are on the version line
      if version_prefix in line:
        version_line = i
        # print("[version found]:" + line.replace("\n",""))
        # get rid of version_prefix and split into [max, min, min2]
        old_version = line.replace(version_prefix, '').split('.')
      # append to the text buffer
      prev_file.append(line) 

  # get rid of quotes and newline char and map to integers
  cleanup = lambda x:int(str(x).replace("\"",'').replace("\n", ""))
  new_version = list(map(cleanup, old_version))

  return new_version, version_line, prev_file

def increment(version):
  # bump up the last version
  version[-1] += 1
  return version

def set_version(prev_file,
                version_line,
                new_version,
                filename='pyproject.toml', 
                version_prefix="version ="):
  
  # map to string and join with dots
  version = ".".join(map(lambda x:str(x), new_version))

  # add prefix and quotes
  version = version_prefix + "\"" + version + "\""

  # replace the version_line on the buffer at the stored index 
  # and add the newline char
  prev_file[version_line] = version + "\n"

  # print("[version updated]:" + version)

  # open the same file to write the buffer out and overwrite
  with open(filename, 'w') as f:
    for line in prev_file:
      f.write(line)

def main(filename=None):
  old_version, version_line, prev_file = get_version(filename=filename)
  new_version = increment(old_version)
  set_version(prev_file, version_line, new_version, filename=filename)
  return new_version

if __name__ == '__main__':
  main()
