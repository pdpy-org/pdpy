#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
import time
import argparse
import traceback
from pdpy_lib 
import Translator, ArgumentException

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
  parser.add_argument("-int", "--internals", default="../pddb/pddb.json")
  # parser.add_argument("-v", "--verbose", action="store_true")

  # get the arguments as a dictionary
  args = parser.parse_args()
  arguments = vars(args)

  # get time before translation
  start_time = time.process_time()
  
  try:
    # create an instance of the Translator class
    print("-"*80)
    direction = args.fro + ' -> ' + args.to
    print("BEGIN:" + " " + str(start_time) + " - " + str(direction))
    print("Creating translator instance...")
    translator = Translator(arguments)
    
    # check if the class was created
    if translator is None:
      raise Exception("Translator could not be created.")
    else:
      # print some nice messages
      print("Done.")
      print("From: " + str(translator.input_file))
      print("To: " + str(translator.output_file))
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
    print("END:" + " " + str(end_time) + " - ELAPSED:" + " " + str(end_time - start_time))

if "__main__" in __name__: main()
