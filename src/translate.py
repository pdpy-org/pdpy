#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import argparse
import traceback
from pdpy import Translator, ArgumentException

def main():
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

  # get the arguments as a dictionary
  args = parser.parse_args()
  arguments = vars(args)
  
  # get time before translation
  start_time = time.process_time()
  
  try:
    # create an instance of the Translator class
    translator = Translator(arguments)
    
    # check if the class was created
    if translator is None:
      raise Exception("Translator could not be created.")
    else:
      # print some nice messages
      direction = translator.source + ' -> ' + translator.target
      print("-"*80)
      print(f"BEGIN: {start_time} - {direction}")
      print(f"From: {translator.input_file}")
      print(f"To: {translator.output_file}")
      # call the translator class (defaults to args)
      translator()

  except ArgumentException as e: print("ERROR with arguments:", e)
  except:
    # print the error message
    print("ERROR:")
    print("_" * 80)
    # print the traceback
    print(traceback.format_exc())
    print("=" * 80)

  finally:
    # store time after translation
    end_time = time.process_time()
    # print the last message with the elapsed time
    print(f"END: {end_time} - ELAPSED: {end_time - start_time}")

if "__main__" in __name__: main()
