#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Convert an XML file to a JSON structured file (PdPy format) """

import json
import xml.etree.ElementTree as ET
from ..classes.pdpy import PdPy
from ..classes.canvas import Canvas
from ..classes.classes import Comment, Edge, PdArray, PdMessage, PdObject, Point
from ..util.utils import log

__all__ = [ "XmlToJson" ]

class XmlToJson:
  """
  Convert XML to Json
  """
  def __init__(self, xml_file):
    self.tree = ET.parse(xml_file)
    self.__root__ = self.tree.getroot()
    self.__xmlroot__ = self.__root__.find('canvas')

    if self.__root__.get('encoding') is None:
      encoding = 'utf-8'
    else:
      encoding = self.__root__.get('encoding')
    
    self.patch = PdPy(self.__root__.get('name'), encoding)

    self.patch.root = Canvas(
                       name   =   self.patch.patchname,
                       vis    =   self.getif( self.__xmlroot__, 'vis' ),
                       screen = [ self.getif( self.__xmlroot__, 'x' ), 
                                  self.getif( self.__xmlroot__, 'y' ) ],
                       dimen  = [ self.getif( self.__xmlroot__, 'width' ), 
                                  self.getif( self.__xmlroot__, 'height' ) ],
                       font   =   self.getif( self.__xmlroot__, 'font' ))


    for child in self.__xmlroot__.findall('*'):
      
      if 'x' == child.tag or 'y' == child.tag or 'width' == child.tag or 'height' == child.tag or 'font' == child.tag: 
        continue
      
      if 'canvas' == child.tag:
        print("Make Canvas", child)
        print(child.find("vis").text)
        self.last = self.patch.root.add(Canvas(
                       name   =   self.patch.patchname,
                       vis    =   int(bool(self.getif( child, 'vis'))),
                       screen = [ self.getif( child, 'x' ), 
                                  self.getif( child, 'y' ) ],
                       dimen  = [ self.getif( child, 'width' ), 
                                  self.getif( child, 'height' ) ],
                       font   =   self.getif( child, 'font' )))
        continue
      
      if 'connect' == child.tag:
        print("Make Connect", child)
        continue
      
      if 'msg' == child.tag:
        print("Make Msg", child)
        continue
      
      print("Make", child.tag)


  def getif(self, x, attrib, t=str):
    if x.find(attrib) is not None:
      # print(x.find(attrib).text)
      return t(x.find(attrib).text)
    else:
      return 0
