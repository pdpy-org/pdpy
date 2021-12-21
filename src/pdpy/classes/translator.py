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

from pdpy.classes.default import Formats, getFormat
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
      if hasattr(self, 'fro'):
        self.source = getFormat(self.fro)
      else:
        self.source = self.input_file.suffix
    
    if self.source.replace('.','') not in Formats:
      raise ArgumentException(f"Source format <{self.source}> is not supported.")

    # default target to JSON if not set
    if not hasattr(self, 'target'):
      self.target = getFormat(getattr(self, 'to', 'json'))

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

    log(0, "Translator initialized")

  def write_xml_ref(self):
    """ The XML reflection logic """
    with open((self.output_file.parent / (self.output_file.stem + '_ref_xml')).with_suffix('pd'), 'w', encoding=self.encoding) as fp:
      fp.write(PdPy(
        name = self.input_file.name,
        encoding = self.encoding,
        pd_lines = self.xml.to_string()
      ).__pd__())

  def write_json_ref(self):
    """ The JSON reflection logic """
    with open((self.output_file.parent / (self.output_file.stem + '_ref_pd')).with_suffix('.json'), 'w', encoding=self.encoding) as fp:
      fp.write(PdPy(
        name = self.input_file.name,
        encoding = self.encoding,
        pd_lines = parsePdBinBuf(self.pdpy.__pd__())
      ).__json__())

  def write_pd_ref(self):
    """ The Pd reflection logic """
    with open((self.output_file.parent / (self.output_file.stem + '_ref')).with_suffix('.pd'), 'w', encoding=self.encoding) as fp:
      fp.write(PdPy(
        name = self.input_file.name,
        encoding = self.encoding,
        json = self.json
      ).__pd__())

  def write_pd(self, out=None):
    """ Writes a Pd representation of the PdPy object to the output file. """
    with open(out or (self.output_file.parent / self.output_file.stem).with_suffix('.pd'), 'w', encoding=self.encoding) as fp:
      fp.write(self.pd)

  def write_json(self, out=None):
    """ Writes a JSON string of the PdPy object to the output file. """
    with open(out or (self.output_file.parent / self.output_file.stem).with_suffix('.json'), 'w', encoding=self.encoding) as fp:
      fp.write(self.json)

  def write_pickle(self, out=None):
    """ Writes a pkl binary file of the PdPy object to the output file. """
    with open(out or (self.output_file.parent / self.output_file.stem).with_suffix('.pkl'), 'wb') as fp:
      pickle_dump(self.json, fp, PICKLE_HIGHEST_PROTOCOL)

  def write_xml(self, out=None):
    """ Writes an XML file of the PdPy object to the output file. """
    self.xml.write(out or (self.output_file.parent / self.output_file.stem).with_suffix('.xml').as_posix(), encoding=self.encoding)

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
  
  def translate(self, target):
    
    if target in ('xml', 'XML', 'Xml'):
      self.xml = self.pdpy.__xml__()
    elif target in ('json', 'JSON', 'Json'):
      self.json = self.pdpy.__json__()
    elif target in ('pd', 'PD', 'Pd', 'puredata', 'PureData', 'PureData'):
      self.pd = self.pdpy.__pd__()
    else:
      raise ValueError(f"Invalid target: {target}")
    
    return self



  def __call__(self):

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
