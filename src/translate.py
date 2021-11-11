#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import argparse
import traceback
from pathlib import Path

from pdpy import Translator, log, getFormat

def quit_help(msg=None):
  parser.print_help(sys.stderr)
  if msg is not None:
    print("_"*80)
    log(2,"REASON:", msg)
  else:
    log(2,"Unknown error...")
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
      log(2, source, target, input_file)
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
  
  direct = source + ' -> ' + target
  start_time = time.process_time()
  print("-"*80)
  log(0, f"BEGIN: {start_time} - {direct}")
  log(0, f"From: {input_file}")
  log(0, f"To: {output_file}")
  
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
    print("=" * 80)
    log(2, f"[{input_file}]: {direct}")
    print("_" * 80)
    print(traceback.format_exc())
    print("=" * 80)

  finally:
    end_time = time.process_time()
    log(0, f"END: {end_time} - ELAPSED: {end_time - start_time}")