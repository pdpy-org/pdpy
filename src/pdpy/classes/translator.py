#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Translator class """

import json
import pickle
from types import SimpleNamespace
import pdpy

__all__ = [ "Translator" ] 

def PdPyEncoder(obj):
  if '__pdpy__' in obj:
    pdpyName = obj['__pdpy__']
    # print(pdpyName, obj)
    # obj = set(map(lambda x:PdPyEncoder(x),obj))
    # this line grabs the class from the module
    # and creates an instance of it
    # passing the json object as the argument
    return getattr(pdpy, pdpyName)(json_dict=obj)
  return obj

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
      self.internals = self.load_json(
        self.internals_file,
        object_hook=lambda o:SimpleNamespace(**o)
      )
      # print(self.internals)
    
    # Load the source file
    if self.source == "pd":

      self.pdpy = pdpy.PdPy(
          name = self.path.name,
          encoding = self.enc,
          pd_lines = pdpy.parsePdFileLines(self.load_pd())
      )
      # 3. return a json string representation from pdpy
      self.json = self.pdpy.toJSON()
      self.xml = pdpy.JsonToXml(self.pdpy)

      if self.reflect:
        self.pd_ref = pdpy.PdPy(
          name = self.path.name,
          encoding = self.enc,
          json_dict = self.json
        ).__pd__

    elif self.source == "json" or self.source == "pkl":

      if self.source == "json":
        json_dict = self.load_json()
      else:
        json_dict = self.load_object()

      self.pdpy = pdpy.PdPy(json_dict=json_dict)
      # log(1,'print dumps')
      self.xml = pdpy.JsonToXml(self.pdpy)
      self.pd = self.pdpy.__pd__

      print("-"*80)
      print("BEFORE PDPY from JSON->PD")
      self.pdpy_ref = pdpy.PdPy(
          name = self.path.name,
          encoding = self.enc,
          pd_lines = self.pd
      )
      self.pdpy_ref.dumps()
      if self.reflect: 
        self.json_ref = self.pdpy_ref.toJSON()
    
    elif self.source == "pdpy":
      
      self.pdpy = pdpy.PdPyParser(
        self.load_pdpy(),
        self.internals,
        name = self.path.name,
        encoding = self.enc
      )
      
      self.pd = self.pdpy.__pd__
      self.json = self.pdpy.toJSON()
      self.xml = pdpy.JsonToXml(self.pdpy)
      if self.reflect:
        pdpy.log(1,"pdpy lang reflection not implemented yet")

    elif self.source == "xml":

      self.pdpy = pdpy.PdPy(
          name = self.path.name,
          encoding = self.enc,
          xml_object = pdpy.XmlToJson(self.load_xml())
      )
      self.json = self.pdpy.toJSON()
      self.pd = self.pdpy.__pd__
      if self.reflect: 
        self.xml_ref = pdpy.JsonToXml(self.pdpy)

    else:
      raise ValueError("Unknown source type: {}".format(self.source))

  def save_json(self, file):
    if self.json is not None:
      with open(file.with_suffix(".json"), 'w', encoding=self.enc) as fp:
        fp.write(self.json)
  
  def save_xml(self, file):
    if self.xml is not None:
      with open(file.with_suffix(".xml"), 'w') as fp:
        fp.write(self.xml.to_string())

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

  def load_pdpy(self):
    with open(self.file, "r", encoding=self.enc) as fp:
      return fp
  
  def load_json(self, file=None, object_hook=PdPyEncoder):
    if file is None:
      file = self.file
    with open(file, "r", encoding=self.enc) as fp:
      return json.load(fp, object_hook=object_hook)

  def load_xml(self, file=None):
    if file is None:
      file = self.file
    with open(file, "r", encoding=self.enc) as fp:
      return fp

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
          pdpy.log(1, "Could not load input file", e)
          self.pd_data = None
    
    finally:

      return self.pd_data
