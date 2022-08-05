#!/bin/bash
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #

# Test if the pd file loads

# The Pure Data directory
# pd=/usr/local/lib/pd
pd=/Users/fd/Development/pure-data/Pd-0.52-1.app/Contents/Resources/bin/pd

pd_flags="-nogui -noverbose -noaudio -nomidi -stderr"

if ! $pd $pd_flags -send ';pd quit' -open $1  2>&1 > /dev/null
then
    echo "ERROR LOADING PD FILE $1"
fi
# test_pd $json_ref
