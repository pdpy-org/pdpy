#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Translator class """

from pathlib import Path
from types import SimpleNamespace
from json import load as json_load
from json import loads as json_loads
from pickle import dump as pickle_dump
from pickle import load as pickle_load
from pickle import HIGHEST_PROTOCOL as PICKLE_HIGHEST_PROTOCOL
from pdpy.classes.base import Base
from pdpy.classes.exceptions import ArgumentException
from pdpy.classes.pdpy import PdPy
from pdpy.parse.parser import PdPyParser
from pdpy.parse.xml2json import XmlToJson

from pdpy.classes.default import getFormat
from pdpy.util.utils import log, parsePdBinBuf, parsePdFileLines
from pdpy.classes.pdpyencoder import PdPyEncoder

__all__ = [ "Translator" ] 

class Translator(Base):
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
  file: str
    The file name or path to the input file.
  
  json: dict
    A dictionary containing the kwargs for the translation.
  
  kwargs:
    The kwargs for the translation with the following keys:
  
  `to`: the target format. Can be `json`, `xml`, `pd`, or `pkl`.
  `fro`: the source format. Can be `json`, `xml`, `pd`, or `pkl`.
  `output`: An output file Path, will be formated using `pathlib.Path`
  `encoding`  (`str`, default is 'utf-8'): Encoding of the input file
  `source`    (`str`, inferred from `input_file`): Source file type
  `reflect`   (`bool`): If set to `True`, performs a reflected translation
  """
  def __init__(self, file, json=None, **kwargs):
    
    if file is None:
      raise ArgumentException("No file specified.")
    
    self.input_file = Path(file)

    # check if the input file exists, exit if not
    if not self.input_file.exists():
      raise ArgumentException(f"File <{self.input_file}> does not exist.")

    if json is not None:
      super().__populate__(self, json)
    else:
      for k,v in kwargs.items():
        setattr(self, k, v)
    
    if not hasattr(self, 'encoding') or self.encoding is None:
      self.encoding = 'utf-8'

    if not hasattr(self, 'source'):
      # grab the source extension from the input file if not set
      self.source = getFormat(self.fro) if hasattr(self, 'fro') else self.input_file.suffix
    
    if not hasattr(self, 'target'):
      self.target = getFormat(self.to) if hasattr(self, 'to') else None

    # prepend a dot '.' to the source and target formats; ie, to get '.json'
    def _dot(f): return f".{f}" if not f.startswith('.') else f
    
    self.source = _dot(self.source)
    self.target = _dot(self.target)

    # exit if the source and target formats are the same
    if self.target == self.source:
      raise ArgumentException("Source and target are the same.")

    # exit if input suffix differs from source
    if self.input_file.suffix != self.source:
      raise ArgumentException(f"Input file <{self.input_file}> suffix does not match with source <{self.source}>")

    if self.target is None:
      log(1, "Target not specified")
    else:
      # if not defined, make the output file from the target and the input file
      if not hasattr(self, 'output') or self.output is None:
        self.output_file = self.input_file.with_suffix(self.target)
        log(1, f"Using <{self.output_file.as_posix()}> as output file")
      else:
        # if defined, make sure it's a Path object
        self.output_file = Path(self.output)

    # exit if output suffix differs from target
    if self.output_file.suffix != self.target:
      raise ArgumentException(f"Output file <{self.output_file}> suffix does not match with source <{self.target}>")
    
    # store the ref path
    self.output_file_ref = self.output_file.parent / (self.output_file.stem + "_ref" + self.source)

    if not hasattr(self, 'reflect'): self.reflect = False

    # store an object containing a pd object database
    if hasattr(self, 'internals'):
      log(0, f"Internals file set to <{self.internals}>")
      self.internals = Path(self.internals)
      if self.internals.exists():
        with open(self.internals, "r", encoding=self.encoding) as fp:
          self.internals=json_load(fp,object_hook=lambda o:SimpleNamespace(**o))
      else:
        log(1, f"Internals file does not exist.")

    log(0, f"Loading file <{self.input_file}>")
    
    if self.source == ".pd":
      pd_file_path = self.input_file.as_posix()
      pd_file = self.load_pd(pd_file_path)
      pd_lines = parsePdFileLines(pd_file)
      self.pdpy = PdPy(
          name = self.input_file.name,
          encoding = self.encoding,
          pd_lines = pd_lines
      )

    elif self.source == ".json":
      with open(self.input_file, "r", encoding=self.encoding) as fp:
        self.pdpy = json_load(fp, object_hook = PdPyEncoder())
      self.pdpy.__jsontree__()

    elif self.source == ".pkl":
      with open(self.input_file, "rb") as fp:
        data = pickle_load(fp, encoding=self.encoding)
        self.pdpy = json_loads(data, object_hook = PdPyEncoder())
      self.pdpy.__jsontree__()
    
    elif self.source == ".pdpy":
      with open(self.input_file, "r", encoding=self.encoding) as fp:
        pdpy_file_pointer = fp
      
      self.pdpy = PdPyParser(
        pdpy_file_pointer,
        self.internals,
        name = self.input_file.name,
        encoding = self.encoding
      )
    
    elif self.source == ".xml":
      with open(self.input_file, "r", encoding=self.encoding) as fp:
        self.pdpy = PdPy(
            name = self.input_file.name,
            encoding = self.encoding,
            xml = fp
        )
    else:
      raise ValueError(f"Unknown source type: {self.source}")
  
    log(0, "Translator initialized")

  def __call__(self, target=None, out=None):
    
    if target is None:
      target = self.target
    
    if out is None:
      out = self.output_file
    else:
      if not isinstance(out, Path):
        out = Path(out)
    
    if target == '.json' or target == '.pkl':
      
      log(0, "Returning a json string representation from pdpy")
      
      self.json = self.pdpy.__json__() # get the json string
      
      if self.json is not None:
        if target == '.json':
          with open(self.output_file, 'w', encoding=self.encoding) as fp:
            fp.write(self.json)
        elif target == '.pkl':
          with open(self.output_file, 'wb') as fp:
            pickle_dump(self.json, fp, PICKLE_HIGHEST_PROTOCOL)

        # the Pd reflection logic when json is the target
        if self.reflect:
          self.pd_ref = PdPy(
            name = self.input_file.name,
            encoding = self.encoding,
            json = self.json
          ).__pd__()
          if self.pd_ref is not None:
            with open(self.output_file_ref, 'w', encoding=self.encoding) as fp:
              fp.write(self.pd_ref)

      else:
        log(2, "No JSON representation available")

    if target == 'pd' and self.pdpy is not None:
      
      log(0, "Returning a pd string representation from pdpy")
      
      self.pd = self.pdpy.__pd__() # get the pd representation
      
      if self.pd is not None:
        with open(self.output_file, 'w', encoding=self.encoding) as fp:
          fp.write(self.pd)
        
        # the Json reflection logic when Pd is the target
        if self.reflect:
          
          self.json_ref = PdPy(
            name = self.input_file.name,
            encoding = self.encoding,
            pd_lines = parsePdBinBuf(self.pd)
           ).__json__()
          
          if self.json_ref is not None:
            with open(self.output_file_ref, 'w', encoding=self.encoding) as fp:
              fp.write(self.json_ref)
      else:
        log(2, "No Pd representation available")
      
    if target == ".xml" and self.pdpy is not None:
      
      log(0, "Returning a XML string representation from pdpy")
      
      self.xml = self.pdpy.__xml__() # get the xml representation
      
      if self.xml is not None:
        self.xml.write(self.output_file.as_posix(), encoding=self.encoding)

        # the Pd reflection logic when xml is the target
        if self.reflect:
          
          self.xml_ref = PdPy(
            name = self.input_file.name,
            encoding = self.encoding,
            xml = self.xml.to_string() # give it an xml string
           ).__pd__()
          
          if self.xml_ref is not None:
            with open(self.output_file_ref, 'w', encoding=self.encoding) as fp:
              fp.write(self.xml_ref)
      else:
        log(2, "No XML representation available")
      
  # end def __call__ -------------------------------------------------------

  def load_pd_data(self, encoding, filename):
    # log(1,"Trying", encoding)
    with open(filename, "r", encoding=encoding) as fp:
      lines = [line for line in fp.readlines()]
    return lines, encoding

  def load_pd(self, filename):
    try:
      data, self.encoding = self.load_pd_data(self.encoding, filename)
    except UnicodeDecodeError:
      try:
        data, self.encoding = self.load_pd_data("ascii", filename)
      except UnicodeDecodeError:
        try:
          data, self.encoding = self.load_pd_data("latin-1", filename)
        except Exception as e:
          data = None
          raise ValueError("Could not load input file", e)
    finally:
      return data