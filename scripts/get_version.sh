#!/bin/bash
# this script turns `version ="0.0.2"` into `pdpy==0.0.2`
grep version $1 > /tmp/ver
awk -v SEP=$2 '{gsub("=","",$2);gsub("\"","",$2);printf("pdpy%s%s",SEP,$2)}' /tmp/ver > /tmp/version
cat /tmp/version