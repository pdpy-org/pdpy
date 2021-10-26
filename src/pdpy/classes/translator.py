#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Translator class """

import json
import pickle
from types import SimpleNamespace

from .pdpy import PdPy

from ..parse.json2pd import PdPyToPureData
from ..parse.parser import PdPyParser
from ..util.utils import log, parsePdBinBuf, parsePdFileLines

__all__ = [ "Translator" , "Formats", "getFormat"]

Formats = {
  "pkl" : [ "pickle", "pkl"],
  "json": [ "json" ],
  "pdpy" : [ "pdpy" ],
  "pd"  : [ "pd", "puredata"],
}

def getFormat(fmt):
  for k,v in Formats.items():
    for f in v:
      if fmt == f:
        return k
  return None

def PdPyEncoder(obj):
  # TODO
  # this should be a custom object hook...
  #
  # if "__type__" in obj:
  #   pdpy = PdPy(name=obj["patchname"], encoding=obj["encoding"])
  #   print(obj["root"])
  #   pdpy.root = obj["root"]
  #   return pdpy
  # else:
  #
  return SimpleNamespace(**obj)

class Translator(object):
  """ This class maintains and translates a `pdpy` Object in memory. 

  Description:
  -------------
  This class loads a file in `.pd` or `.json` formats and keeps an
  internal mirror (aka, translation) between the two. The direction
  of the translation depends on the input file type. Use the `save_*`
  functions to write translations to disk. Alternatively, you can load 
  a `.pkl` (aka, pickle) file  containing a `pdpy` object.

  Inputs:
  --------
  `input_file` (`Path`):
    - An input file Path, using `pathlib.Path`
  `encoding`  (`str`, default is 'utf-8'):
    - Encoding of the input file
  `source`    (`str`, inferred from `input_file`):
    - Source file type
  `reflect`   (`bool`): 
    - If set to `True`, performs a reflected translation: pd -> json -> pd
  """
  def __init__(self, input_file, 
              encoding='utf-8', 
              source=None, 
              reflect=False, 
              internals=None):
    
    self.path = input_file
    self.file = self.path.as_posix()
    self.source = source if source is not None else self.path.suffix
    self.reflect = reflect
    self.enc = encoding
    
    if internals is not None:
      # store an object containing a pd object database
      self.internals_file = internals
      self.internals = self.load_json(self.internals_file)
      # print(self.internals)
    
    # initialize an empty pdpy instance with name and encoding
    self.pdpy = PdPy(self.path.name, self.enc)
    
    # Load the source file
    if self.source == "pd":

      # 1. load the pd file in memory
      self.pd = self.load_pd()
      # 2. parse the pd lines and populate the pdpy instance
      # account for pure data line endings and split into a list
      self.pdpy.parse( parsePdFileLines(self.pd) )
      # 3. return a json string representation from pdpy
      self.json = self.pdpy.toJSON()
      if self.reflect: self.pd_ref = PdPyToPureData(self.pdpy)

    elif self.source == "pkl":

      self.json = self.load_object()
      self.pd = PdPyToPureData(self.json)
      self.pd_data = parsePdBinBuf(self.pd)
      self.pdpy.parse( self.pd_data )
      if self.reflect: self.json_ref = self.pdpy.toJSON()

    elif self.source == "json":
       
      self.json = self.load_json()
      self.pd = PdPyToPureData(self.json)
      self.pdpy.parse( parsePdBinBuf(self.pd) )
      if self.reflect: self.json_ref = self.pdpy.toJSON()

    elif self.source == "pdpy":
      
      self.pdpy = self.load_pdpy(self.path.name,self.enc)
      # self.pdpy.dumps()
      self.pd = PdPyToPureData(self.pdpy)
      self.json = self.pdpy.toJSON()

    else:
      log(2,f"Can't parse source file: {input_file}")
      return None


  def save_json(self, file):
    if self.json is not None:
      with open(file.with_suffix(".json"), 'w', encoding=self.enc) as fp:
        fp.write(self.json)
  
  def save_pd_reflection(self, file):
    if self.reflect and self.pd_ref is not None:
      file = file.parent / (file.stem + '_ref')
      with open(file.with_suffix(".pd"), 'w', encoding=self.enc) as fp:
        fp.write(self.pd_ref)

  def save_pd(self, file):
    if self.pd is not None:
      with open(file, 'w', encoding=self.enc) as fp:
        fp.write(self.pd)
  
  def save_json_reflection(self, file):
    if self.reflect and self.json_ref is not None:
      file = file.parent / (file.stem + '_ref')
      with open(file.with_suffix(".json"), 'w', encoding=self.enc) as fp:
        fp.write(self.json_ref)

  def save_object(self, file):
    if self.json is not None:
      with open(file.with_suffix(".pkl"), "wb") as fp:
        pickle.dump(self.json, fp, pickle.HIGHEST_PROTOCOL)

  def load_pdpy(self, name, encoding):
    with open(self.file, "r", encoding=self.enc) as fp:
      return PdPyParser(fp, self.internals, name=name, encoding=encoding)
  
  def load_json(self, file=None):
    if file is None:
      file = self.file
    with open(file, "r", encoding=self.enc) as fp:
      return json.load(fp, object_hook = PdPyEncoder)
  
  def load_object(self):
    with open(self.file, "rb") as fp:
      data = pickle.load(fp, encoding=self.enc)
      return json.loads(data, object_hook = PdPyEncoder)

  def load_pd_data(self, encoding):
    # log(0,"Trying", encoding)
    with open(self.file, "r", encoding=encoding) as fp:
      lines = [line for line in fp.readlines()]
    return lines, encoding

  def load_pd(self):
    
    try:
      self.pd_data, self.enc = self.load_pd_data(self.enc)
    
    except UnicodeDecodeError:
      try:
        self.pd_data, self.enc = self.load_pd_data("ascii")
      except UnicodeDecodeError:
        try:
          self.pd_data, self.enc = self.load_pd_data("latin-1")
        except Exception as e:
          log(1, "Could not load input file", e)
          self.pd_data = None
    
    finally:

      return self.pd_data
