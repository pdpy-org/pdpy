#!/bin/bash

DICT=import_dict.json
echo "{" > $DICT; 
for i in *.py;
do
  grep ^class $i | 
  cut -f 2 -d ' ' | 
  awk -F "(" -v file=$i '{
    gsub(".py","",file);
    gsub(":|)","",$0);
    printf "  \"%s\" : {\n  \"__file__\" : \"%s\",\n \"__subclass__\" : \"%s\"\n},\n",$1,file,$2
    }' >> $DICT
done
echo "}" >> $DICT
