#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" 
Translator
==========
"""

from pathlib import Path
from json import load as json_load
from json import loads as json_loads
from pickle import dump as pickle_dump
from pickle import load as pickle_load
from pickle import HIGHEST_PROTOCOL as PICKLE_HIGHEST_PROTOCOL
from types import SimpleNamespace

from ..core.base import Base
from ..patching.pdpy import PdPy
from ..encoding.pdpyencoder import PdPyEncoder
from ..parse.pdpyparser import PdPyParser
from ..utilities.default import getFormat
from ..utilities.exceptions import ArgumentException
from ..utilities.utils import log, parsePdFileLines, loadPdFile, parsePdBinBuf

__all__ = [ 'Translator' ] 

class Translator(Base):
  r""" This class maintains and translates a `pdpy` Obj in memory. 

  This class loads a file in `.pd` or `.json` formats and keeps an
  internal mirror (aka, translation) between the two. The direction
  of the translation depends on the input file type. Use the `save_*`
  functions to write translations to disk. Alternatively, you can load 
  a `.pkl` (aka, pickle) file  containing a `pdpy` object.

  Parameters
  ----------
  json: :class:`dict`
    A dictionary of arguments with the following keys:
    
    *  ``to``: the target format. Can be `json`, `xml`, `pd`, or `pkl`.
    *  ``fro``: the source format. Can be `json`, `xml`, `pd`, or `pkl`.
    *  ``input``: An input file Path, will be formated using `pathlib.Path`
    *  ``output``: An output file Path, will be formated using `pathlib.Path`
    *  ``encoding`` (`str`, defaults: 'utf-8'): Encoding of the input file
    *  ``source`` (`str`, inferred from `input_file`): Source file type
    *  ``reflect`` (`bool`): If set to `True`, performs a reflected translation
  """
  def __init__(self, json):

    super().__populate__(self, json)
    
    self.source = getFormat(self.fro) if self.fro else None
    self.target = getFormat(self.to) if self.to else None
    
    # grab the source extension from the input file
    if self.source is None:
      self.source = self.input_file.suffix

    if self.target == self.source:
      raise ArgumentException("Source and target are the same, skipping translation")

    if self.target is None:
      raise ArgumentException("To or fro are missing or malformed")
    else:
      self.input_file = Path(self.input)
      if self.input_file.suffix != "." + self.source:
        log(2, self.source, self.target, self.input_file)
        raise ArgumentException("Input file suffix does not match with -f argument")
      if not self.input_file.exists():
        raise ArgumentException("File" + " " + self.input_file + " " + "does not exist.")
      if self.output is None:
        self.output_file = self.input_file.with_suffix("." + self.target)
        log(1, "Using" + " " + self.output_file.as_posix() + " " + "as output file")
      else:
        self.output_file = Path(self.output)
        if self.output_file.suffix != "." + self.target:
          raise ArgumentException("Input file suffix does not match with -f argument")
    
    # store an object containing a pd object database
    if self.internals is not None:
      r"""  Attempt to load PDDB manager

      Fall back to json if the package is not there.
      Get it here: `<https://github.com/pdpy-org/pddb>`_
      """
      import sys
      pddb_path = Path(self.internals)
      if pddb_path.exists():
        try:
          sys.path.append((pddb_path.parent / 'src').as_posix())
          from pddb import PDDB
          self.pddb = PDDB(dbname=pddb_path.resolve(), listen=False)
        except ImportError:
          print("Could not import pddb. Loading json instead.")
          try:
            with open(self.internals, "r", encoding=self.encoding) as fp:
              self.pddb=json_load(fp,object_hook=lambda o:SimpleNamespace(**o))
          except Exception as e:
            print("Could not load pddb.json. See error below.")
            print(e)
      else:
        raise ArgumentException("PDDB:" + " " + pddb_path.as_posix() + " " + "is missing.")

    # Load the source file
    
    if self.source == "pd":
      pd_file_path = self.input_file.as_posix()
      pd_file = loadPdFile(pd_file_path, self.encoding)
      pd_lines = parsePdFileLines(pd_file)
      self.pdpy = PdPy(
          name = self.input_file.name,
          encoding = self.encoding,
          pd_lines = pd_lines
      )

    elif self.source == "json":
      with open(self.input_file, "r", encoding=self.encoding) as fp:
        self.pdpy = json_load(fp, object_hook = PdPyEncoder())
      self.pdpy.__jsontree__()

    elif self.source == "pkl":
      with open(self.input_file, "rb") as fp:
        data = pickle_load(fp, encoding=self.encoding)
        self.pdpy = json_loads(data, object_hook = PdPyEncoder())
      self.pdpy.__jsontree__()
    
    elif self.source == "pdpy":
      with open(self.input_file, "r", encoding=self.encoding) as fp:
        self.pdpy = PdPyParser(
          fp.readlines(), # pdpy_file_pointer
          self.pddb,
          name = self.input_file.name,
          encoding = self.encoding
        )
    
    elif self.source == "xml":
      with open(self.input_file, "r", encoding=self.encoding) as fp:
        self.pdpy = PdPy(
            name = self.input_file.name,
            encoding = self.encoding,
            xml = fp
        )
    else:
      raise ValueError("Unknown source type: {}".format(self.source))
  

  def __call__(self, target=None, out=None):
    
    if target is None:
      target = self.target
    
    if out is None:
      out = self.output_file
    
    if not isinstance(out, Path):
      out = Path(out)
    
    if target == 'json' or target == 'pkl':
      # return a json string representation from pdpy
      self.json = self.pdpy.__json__()
      if self.json is not None:
        if target == 'json':
          ofname = out.with_suffix(".json")
          with open(ofname, 'w', encoding=self.encoding) as fp:
            fp.write(self.json)
        elif target == "pkl":
          ofname = out.with_suffix(".pkl")
          with open(out.with_suffix(".pkl"), "wb") as fp:
            pickle_dump(self.json, fp, PICKLE_HIGHEST_PROTOCOL)

        # the Pd reflection logic when json is the target
        if self.reflect:
          self.pd_ref = PdPy(
            name = self.input_file.name,
            encoding = self.encoding,
            json = self.json
          ).__pd__()
          if self.pd_ref is not None:
            out = out.parent / (out.stem + '_ref')
            ofname = out.with_suffix(".pd")
            with open(ofname, 'w', encoding=self.encoding) as fp:
              fp.write(self.pd_ref)

      else:
        log(2, "No JSON representation available")

    if target == "pd" and self.pdpy is not None:
      # get the pd representation
      self.pd = self.pdpy.__pd__()
      if self.pd is not None:
        with open(out, 'w', encoding=self.encoding) as fp:
          fp.write(self.pd)
        # the Json reflection logic when Pd is the target
        if self.reflect:
          self.json_ref = PdPy(
            name = self.input_file.name,
            encoding = self.encoding,
            pd_lines = parsePdBinBuf(self.pd)
           ).__json__()
          if self.json_ref is not None:
            out = out.parent / (out.stem + '_ref')
            ofname = out.with_suffix(".json")
            with open(ofname, 'w', encoding=self.encoding) as fp:
              fp.write(self.json_ref)
      else:
        log(2, "No Pd representation available")
      
    if target == "xml" and self.pdpy is not None:
      # get the xml representation
      self.xml = self.pdpy.__xml__()
      if self.xml is not None:
        ofname = out.with_suffix(".xml")
        self.xml.write(ofname.as_posix(), encoding=self.encoding)

        # the Pd reflection logic when xml is the target
        if self.reflect:
          self.xml_ref = PdPy(
            name = self.input_file.name,
            encoding = self.encoding,
            xml = self.xml.to_string() # give it an xml string
           ).__pd__()
          if self.xml_ref is not None:
            out = out.parent / (out.stem + '_ref')
            ofname = out.with_suffix(".pd")
            with open(ofname, 'w', encoding=self.encoding) as fp:
              fp.write(self.xml_ref)
      else:
        log(2, "No XML representation available")
      
      # self.xml = JsonToXml(self.pdpy)
      # if self.xml is not None:
      #   ofname = out.with_suffix(".xml")
      #   with open(ofname, 'w') as fp:
      #     fp.write(self.xml.to_string())
      #   if self.reflect:
      #      self.xml_ref = JsonToXml(self.pdpy)

  # end def __call__
