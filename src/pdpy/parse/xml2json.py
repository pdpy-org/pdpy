#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Convert an XML file to a JSON structured file (PdPy format) """

import json
import xml.etree.ElementTree as ET
from ..classes.pdpy import PdPy
from ..classes.canvas import Canvas
from ..classes.classes import Comment, Edge, PdArray, PdMessage, PdNativeGui, PdObject, Point
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

    # add the root canvas
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
        __canvas__ = self.patch.__get_canvas__()
        canvas = Canvas(name   =   self.patch.patchname,
                        vis    =   int(bool(self.getif( child, 'vis'))),
                        id     = self.patch.__obj_idx__,
                        screen = [ self.getif( child, 'x' ), 
                                  self.getif( child, 'y' ) ],
                        dimen  = [ self.getif( child, 'width' ), 
                                  self.getif( child, 'height' ) ],
                        font   =   self.getif( child, 'font' ))
        self.patch.__canvas_idx__.append(__canvas__.add(canvas))
        continue
      
      if 'comment' == child.tag:
        self.patch.__last_canvas__().comment(Comment(
          child.find('x').text, 
          child.find('y').text,
          child.text))
        continue
      
      if 'connect' == child.tag:
        self.patch.__last_canvas__().edge(Edge( 
          child.find('source').find('id').text,
          child.find('source').find('port').text,
          child.find('sink').find('id').text,
          child.find('sink').find('port').text))
        continue
      
      if 'msg' == child.tag:
        self.patch.__obj_idx__ = self.patch.__last_canvas__().grow()
        msg = PdMessage(
          self.patch.__obj_idx__,
          child.find('x').text,
          child.find('y').text)
        for t in child.findall('target'):
          msg.addTarget(t.text)
          for m in t.findall('message'):
            msg.targets[-1].add(m.text)
        
        self.patch.__last_canvas__().add(msg)
        continue
      
      if 'floatatom' == child.tag or 'symbolatom' == child.tag or 'listbox' == child.tag:
        print( "Make PdNativeGui", child.tag)
        self.patch.__last_canvas__().add(
        #   PdNativeGui(child.tag, 
        #               child.find('x').text, 
        #               child.find('y').text, 
        #               child.find('width').text, 
        #               child.find('height').text, 
        #               child.find('font').text, 
        #               child.find('label').text, 
        #               child.find('value').text))
        # )
        continue

      print("Make", child.tag)


  def getif(self, x, attrib, t=str):
    if x.find(attrib) is not None:
      # print(x.find(attrib).text)
      return t(x.find(attrib).text)
    else:
      return 0
