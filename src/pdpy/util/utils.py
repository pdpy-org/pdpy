#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Utilities """

import sys
import re

__all__ = [
  "log",
  "splitAtChar",
  "splitByEscapedChar",
  "parsePdBinBuf",
  "parsePdFileLines",
  "printer",
  "checknum",
  "quit_help"
]

def checknum(num):
  try:
    int(num)
    return True
  except ValueError:
    try:
      float(num)
      return True
    except ValueError: return False


# def printer2(argument):
#   def decorator(function):
#     def wrapper(*args, **kwargs):
#       log(0, argument)
#       result = function(*args, **kwargs)
#       return result
#     return wrapper
#   return decorator


def printer(func):
  def wrapper(*arg):
    # log(0, func.__name__)
    result = func(*arg)
    if result:  
      # log(0, "="*80)
      log(0, func.__name__, repr(arg[1:] if 1 < len(arg) else arg))
    return result
  return wrapper

# def log_decorator(func):
#   def wrapper(*arg):
#     # log(0, func.__name__)
#     result = func(*arg)
#     if result:  
#       print("="*80)
#       print(func.__file__, func.__name__, repr(*arg))
#     return result
#   return wrapper

# @log_decorator
def log(l, *argv):
  """ log utility with level and variable arguments

  Description
  -----------
  This function printst to console with error `level` 
  """
  if 1==l:
    print("WARNING:",*argv)
  elif 2==l:
    print("ERROR:",*list(map(lambda x:x.__repr__(),argv)))
  else:
    print(*argv)

def findIndices(data, cond_func):
  """ Find the start and stop slice indices 
  of elements in a list that satisfy a condition function `cond_func`

  Returns
  -------
  list of tuples (start, stop)

  Example
  -------
  `indices = findIndices(data, lambda x: not len(x))`

  """

  indices = []
  start_index = 0
  for stop_index, datum in enumerate(data):
    if cond_func(datum):
      indices.append((start_index, stop_index))
      start_index = stop_index + 1
  return indices

def splitByNone(data):
  """ Split a list by None elements

  Description
  -----------
  This function splits a list by None elements
  and returns a list of lists
  """
  
  indices = findIndices(data, lambda x: not len(x))

  if not len(indices): return data
  else:
    # if there are indices, split the list
    # iterate over the indices and split accordingly
    return [ data[i[0]:i[1]] for i in indices ]


def splitByEscapedChar(data, char=";"):
  """ Split a string by escaped char

  Description
  -----------
  This function splits a string by escaped char
  and returns a list of lists or the original string

  Parameters
  ----------
  data : list
    list to be split
  char : str
    char to split by (default ";")

  """

  regex = r"(?<=\\)" + re.escape(char)
  idx = [i for i, d in enumerate(data) if re.search(regex,d) ]

  if not len(idx): 
    return data
  else:
    result = [list(data[1+idx[i]:idx[i+1]]) for i in range(len(idx)-1)]
    # result = list(filter(None,result)) # do not filter out empty elements
    
    # account for the first index
    if len(data[:idx[0]]):
      if not re.search(regex, " ".join(data[:idx[0]])):
        result = [" ".join(data[:idx[0]])] + result

    return result

def splitSemi(argv):
  lines = []
  line = ''
  if "\\;" in argv:
    for arg in argv:
      if arg == "\\;":
        lines.append(line)
        line = ''
      else:
        if line == '': line += arg
        else: line += ' ' + arg
    lines.append(line)
  else:
    lines = [" ".join(argv)]
  lines = list(filter(None, lines))
  return lines

def splitAtChar(line, char=",", escaped=True, double=False):

  if escaped:
    if double:
      regex = r"(?<=\\\\)" + re.escape(char)
      # offset = 4
    else:
      regex = r"(?<=\s\\)" + re.escape(char)
      # offset = 2
  else:
    regex = r"(?<!\\)" + re.escape(char)
    # offset = 0
  result = re.split(regex,line)

  return result

def tokenize(line):
  # account for comma chararcter delimiting obj border box
  line = splitAtChar(line, escaped=False)

  if len(line) == 2:
    tokens = []
    for t in line:
      tokens += splitAtChar(t, char=" ", escaped=False)
  else:
    tokens = splitAtChar(line[0], char=" ", escaped=False)

  # filter out empty tokens
  tokens = list(filter(None,tokens))

  return tokens

def parsePdFileLines(file_lines):
  """ Feed in file lines and return a list with pure data lines

  Description
  -----------
  This function returns a nodes list containing
  pure data lines split by the semicolon char,
  accounting specially for lines that span multiple rows 
  """
  pd_start = re.compile(r"^#[XNA]", re.MULTILINE)  

  lines = []
  for line in file_lines:
    line = line.strip()
    if re.search(pd_start, line): lines.append(line)
    else:
      # line does not start in a pd-way
      # append to the last stored line
      if len(line): lines[-1] += ' ' + line

  nodes = [ tokenize(line[:-1]) for line in lines ]

  return  nodes

def parsePdBinBuf(binbuf):
  """ Feed in a pd file string and return a list with pure data lines

  Description
  -----------
  This function returns a nodes list containing
  pure data lines split by the semicolon char,
  accounting specially for lines that span multiple rows 
  """
  pd_start = re.compile(r"(#[XNA].*);(?=\r\n)")
  lines = re.findall(pd_start, binbuf)
  nodes = [ tokenize(line) for line in list(filter(None,lines)) ]

  return  nodes

def quit_help(msg=None, parser=None):
  if parser is not None:
    parser.print_help(sys.stderr)
  if msg is not None:
    print("_"*80)
    log(2,"REASON:", msg)
  else:
    log(2,"Unknown error...")
  sys.exit(1)
