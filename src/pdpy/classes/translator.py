#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Translator class """

import json
import pickle
from pdpy.classes.base import Base
from pdpy.classes.exceptions import ArgumentException
from pdpy.classes.pdpy import PdPy
from pdpy.parse.parser import PdPyParser
from pdpy.parse.xml2json import XmlToJson
from pdpy.parse.json2xml import JsonToXml
from pdpy.classes.default import getFormat
from pdpy.util.utils import PdPyEncoder, log, parsePdBinBuf, parsePdFileLines
from pathlib import Path
from types import SimpleNamespace

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
  A dictionary of arguments with the following keys:
  `to`: the target format. Can be `json`, `xml`, `pd`, or `pkl`.
  `fro`: the source format. Can be `json`, `xml`, `pd`, or `pkl`.
  `input`: An input file Path, will be formated using `pathlib.Path`
  `output`: An output file Path, will be formated using `pathlib.Path`
  `encoding`  (`str`, default is 'utf-8'): Encoding of the input file
  `source`    (`str`, inferred from `input_file`): Source file type
  `reflect`   (`bool`): If set to `True`, performs a reflected translation
  """
  def __init__(self, json_dict):

    super().__populate__(self, json_dict)
    
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
        raise ArgumentException(f"File {self.input_file} does not exist.")
      if self.output is None:
        self.output_file = self.input_file.with_suffix("." + self.target)
        log(1, f"Using {self.output_file.as_posix()} as output file")
      else:
        self.output_file = Path(self.output)
        if self.output_file.suffix != "." + self.target:
          raise ArgumentException("Input file suffix does not match with -f argument")
    
    # store an object containing a pd object database
    if self.internals is not None:
      with open(self.internals, "r", encoding=self.encoding) as fp:
        self.internals=json.load(fp,object_hook=lambda o:SimpleNamespace(**o))
      # print(self.internals)
    

    # Load the source file
    
    if self.source == "pd":
      self.pdpy = PdPy(
          name = self.input_file.name,
          encoding = self.encoding,
          pd_lines = parsePdFileLines(self.load_pd(self.input_file.as_posix()))
      )

    elif self.source == "json":
      with open(self.input_file, "r", encoding=self.encoding) as fp:
        self.pdpy = json.load(fp, object_hook = PdPyEncoder())
      self.pdpy.__tree__()

    elif self.source == "pkl":
      with open(self.input_file, "rb") as fp:
        data = pickle.load(fp, encoding=self.encoding)
        self.pdpy = json.loads(data, object_hook = PdPyEncoder())
      self.pdpy.__tree__()
    
    elif self.source == "pdpy":
      with open(self.input_file, "r", encoding=self.encoding) as fp:
        pdpy_file_pointer = fp
      
      self.pdpy = PdPyParser(
        pdpy_file_pointer,
        self.internals,
        name = self.input_file.name,
        encoding = self.encoding
      )
    
    elif self.source == "xml":
      #TODO: here is the problem, 
      # xml should load from within the PdPy class
      # now it's loading inside the XmlToJson class, 
      # which loads and populates an internal PdPy class
      
      with open(self.input_file, "r", encoding=self.encoding) as fp:
        self.pdpy = XmlToJson(fp)
      # self.pdpy = PdPy(
      #     name = self.input_file.name,
      #     encoding = self.encoding,
      #     xml_object = )
      # )
    
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
            pickle.dump(self.json, fp, pickle.HIGHEST_PROTOCOL)

        # the Pd reflection logic when json is the target
        if self.reflect:
          self.pd_ref = PdPy(
            name = self.input_file.name,
            encoding = self.encoding,
            json_dict = self.json
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
      self.xml = JsonToXml(self.pdpy)
      if self.xml is not None:
        ofname = out.with_suffix(".xml")
        with open(ofname, 'w') as fp:
          fp.write(self.xml.to_string())
        if self.reflect:
           self.xml_ref = JsonToXml(self.pdpy)

  # end def __call__

  def load_pd_data(self, encoding, filename):
    # log(1,"Trying", encoding)
    with open(filename, "r", encoding=encoding) as fp:
      lines = [line for line in fp.readlines()]
    return lines, encoding

  def load_pd(self, filename):
    try:
      self.pd_data, self.encoding = self.load_pd_data(self.encoding, filename)
    except UnicodeDecodeError:
      try:
        self.pd_data, self.encoding = self.load_pd_data("ascii", filename)
      except UnicodeDecodeError:
        try:
          self.pd_data, self.encoding = self.load_pd_data("latin-1", filename)
        except Exception as e:
          self.pd_data = None
          raise ValueError("Could not load input file", e)
    finally:
      return self.pd_data