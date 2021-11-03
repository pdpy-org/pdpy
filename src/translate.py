#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import traceback
from pathlib import Path

from pdpy import Translator, log, getFormat

def quit_help(msg=None):
  parser.print_help(sys.stderr)
  if msg is not None:
    log(2, "-"*80)
    log(2,"REASON:", msg)
  log(2,"-"*80)
  sys.exit(1)

global internals
internals = {}

if "__main__" in __name__:
  parser = argparse.ArgumentParser(
  description = """
  Convert Pure Data (.pd) files to and from JSON-formatted files.
  """)

  parser.add_argument("-i", "--input")
  parser.add_argument("-f", "--fro")
  parser.add_argument("-t", "--to")
  parser.add_argument("-r", "--reflect", action='store_true')
  parser.add_argument("-e", "--encoding", default='utf-8')
  parser.add_argument("-o", "--output", default=None)
  parser.add_argument("-int", "--internals", default="internals/pddb.json")
  # parser.add_argument("-v", "--verbose", action="store_true")

  args = parser.parse_args()
  
  source = getFormat(args.fro) if args.fro else None
  target = getFormat(args.to) if args.to else None
  
  if source is None or target is None:
    quit_help("To or fro are missing or malformed")
  else:
    input_file = Path(args.input)
    if input_file.suffix != "." + source:
      print(source, target, input_file)
      quit_help("Input file suffix does not match with -f argument")
    if not input_file.exists():
      quit_help(f"File {input_file} does not exist.")
    if args.output is None:
      output_file = input_file.with_suffix("." + target)
      log(1, f"Using {output_file.as_posix()} as output file")
    else:
      output_file = Path(args.output)
      if output_file.suffix != "." + target:
        quit_help("Input file suffix does not match with -f argument")
  log(0, source, '->', target)
  log(0, input_file, "->", output_file)
  
  try:
    trans = Translator(input_file, 
                       encoding = args.encoding, 
                       source   = source, 
                       reflect  = args.reflect, 
                       internals = args.internals)

    if target == "json":
      trans.save_json(output_file)
      if trans.reflect:
        trans.save_pd_reflection(output_file)
    
    if target == "xml":
      trans.save_xml(output_file)

    if target == "pkl":
      trans.save_object(output_file)
    
    if target == "pd":
      trans.save_pd(output_file)

      if trans.reflect:
        trans.save_json_reflection(output_file)

  except:
    log(2, "-" * 80)
    log(2, f"Input: {input_file}")
    log(2, "-" * 80)
    traceback.print_exc()
