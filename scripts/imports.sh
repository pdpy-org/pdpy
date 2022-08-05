#!/bin/bash
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
if [ ! $1 ]; then
    echo "Usage: ./imports.sh <path_to_pdpy_repo>"
    exit 1
fi

cd "$1"
find . -name '*.py' | 
awk -F '/' '
!/__init__/{
  if ($3)
  {
    a = "."
  } else {
    a = ""
  };
  printf "from .%s%s%s import *\n", $2, a, $3
}' |
sed 's/\.py//g' 
cd "$OLDPWD"