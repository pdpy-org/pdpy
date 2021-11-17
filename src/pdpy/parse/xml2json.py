#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Convert an XML file to a JSON structured file (PdPy format) """

import xml.etree.ElementTree as ET

from ..util.utils import log
from ..classes.base import Base
from ..classes.pddata import PdData
from ..classes.iemgui import PdIEMGui
from ..classes.pdpy import PdPy
from ..classes.default import Default, IEMGuiNames, XmlTagConvert
from ..classes.canvas import Canvas
from ..classes.message import PdMessage
from ..classes.data_structures import *
from ..classes.comment import Comment
from ..classes.connections import Edge
from ..classes.pdarray import PdArray
from ..classes.pdobject import PdObject
from ..classes.gui import PdNativeGui
# from ..classes.dependencies import Dependencies
from ..classes.classes import Coords
# from ..util.utils import log

__all__ = [ "XmlToJson" ]

class XmlToJson(Base):
  """
  Convert XML to Json
  """
  def __init__(self, xml_file):
    self.tree = ET.parse(xml_file)
    self.__d__ = Default()
    self.__conv__ = XmlTagConvert()
    self.__root__ = self.tree.getroot()
    self.__x__ = self.__root__.find('canvas')
    if self.__root__.get('encoding') is None:
      encoding = 'utf-8'
    else:
      encoding = self.__root__.get('encoding')
    
    self.patch = PdPy(self.__root__.get('name'), encoding)

    # add the root canvas
    self.patch.root = Canvas(json_dict={
      'name' : self.patch.patchname,
      'vis' : self.__x__.findtext('vis', default=self.__d__.vis),
      'screen' : [
        self.__x__.findtext('x', default=self.__d__.screen['x']), 
        self.__x__.findtext('y', default=self.__d__.screen['x'])
      ],
      'dimen'  : [
        self.__x__.findtext('width', default=self.__d__.dimen['width']),
        self.__x__.findtext('height',default=self.__d__.dimen['height'])
      ],
      'font' : self.__x__.findtext('font', default=self.__d__.font['size']),
      'isroot': True
    })

    # NOTE: add struct to root, not to canvas root
    for child in self.tree.findall('struct/template'):
      self.patch.addStruct(child, source='xml')

    for child in self.tree.findall('declare/path'):
      self.patch.addDependencies(['-path', child.text])
    
    for child in self.tree.findall('declare/lib'):
      self.patch.addDependencies(['-lib', child.text])

    for child in self.__x__.findall('*'):
      if child is not None:
        self.addNodes(child, self.patch.root)
        self.addComments(child, self.patch.root)
        self.addConnections(child, self.patch.root)

  def addComments(self, x, __last_canvas__):
    if 'comment' == x.tag:
      __last_canvas__.comment(Comment(xml_object=x))
      return

  def addConnections(self, x, __last_canvas__):
    if 'connect' == x.tag:
      __last_canvas__.edge(Edge(xml_object=x))

  def addCanvas(self, node):
    __canvas__ = self.patch.__get_canvas__()
    canvas = Canvas(
      name = node.findtext('name', default=self.__d__.name),
      vis = node.findtext('vis', default=self.__d__.vis),
      id  = node.get('id', default=self.patch.__obj_idx__),
      screen = [
        node.findtext('x', default=self.__d__.screen['x']), 
        node.findtext('y', default=self.__d__.screen['x'])
      ],
      dimen  = [
        node.findtext('width', default=self.__d__.dimen['width']),
        node.findtext('height',default=self.__d__.dimen['height'])
      ],
      font=node.findtext('font', default=self.__d__.font['size']),
    )
    
    canvas.title=node.findtext('title', default=self.__d__.name)
    canvas.addpos(node.find('position').findtext('x'), node.find('position').findtext('y'))
    self.patch.__canvas_idx__.append(__canvas__.add(canvas))
    
    for child in node.findall('*'):
      if child is not None:
        self.addNodes(child, canvas)
        self.addComments(child, canvas)
        self.addConnections(child, canvas)
  # end of addCanvas -----------------------------------------------------------
  
  def addScalar(self, x, __last_canvas__):
    scalar = Scalar(struct=self.patch.struct, xml_object=x)
    __last_canvas__.add(scalar)

  def addGOPArray(self, x, __last_canvas__):
    # log(1, "goparray", x)
    arr = PdType(json_dict={
      'name' : x.findtext('name'),
      'size' : x.findtext('size'),
      'type' : x.findtext('type'),
      'flag' : x.findtext('flag'),
      'className' : x.tag
    })
    _data = x.find('data')
    if _data: 
      setattr(arr, 'data', PdData(list(map(lambda x:x.text, _data.findall('float')))))
    __last_canvas__.add(arr)


  def addCoords(self, x, __last_canvas__):
    # log(1, "coords", x)
    __last_canvas__.coords = Coords(xml_object=x)

  def addNodes(self, x, __last_canvas__):
    border = None # the border of the object box
    if x.tag in ['vis', 'x', 'y', 'width', 'height', 'font', 'title', 'name', 'connect', 'comment', 'position', 'area', 'limits', 'struct']:
      return
    elif 'canvas' == x.tag:
      self.addCanvas(x)
    elif 'coords' == x.tag:
      self.addCoords(x, __last_canvas__)
    elif 'scalar' == x.tag:
      self.addScalar(x, __last_canvas__)
    elif 'goparray' == x.tag:
      self.addGOPArray(x, __last_canvas__)
    elif 'border' == x.tag:
      border = x.text
    elif 'isroot' == x.tag:
      __last_canvas__.isroot = self.pdbool(x.text)
    elif x.find('x') is None:
      log(1, "Unknown Tag:", x.tag)
    else:
      self.patch.__obj_idx__ = __last_canvas__.grow()
      __id__   = int(x.get('id', default = self.patch.__obj_idx__ ))
      __xpos__ = int(x.findtext('x'))
      __ypos__ = int(x.findtext('y'))
      
      if 'msg' == x.tag:
        obj = PdMessage(pd_lines=[__id__, __xpos__, __ypos__])
        for t in x.findall('target'):
          obj.addTarget(t.text)
          for m in t.findall('message'):
            obj.targets[-1].add(m.text)
        # add the message and do not continue loading
        if border: obj.border = border
        __last_canvas__.add(obj)
        return
      
      elif x.tag in ['floatatom', 'symbolatom', 'listbox']:
        # print( "Make PdNativeGui", x.tag)
        obj = PdNativeGui(
          className=x.tag, 
          pd_lines=[
            __id__, __xpos__, __ypos__,
            x.findtext('digits_width', default=self.__d__.digits_width),
            x.findtext('lower', default=self.__d__.limits['lower']),
            x.findtext('upper', default=self.__d__.limits['upper']),
            x.findtext('flag', default=self.__d__.flag),
            x.findtext('label', default=self.__d__.label),
            x.findtext('receive', default=self.__d__.receive),
            x.findtext('send', default=self.__d__.send)
        ])
      
      # text or array-group objects
      elif x.tag in ['text', 'array']:
        obj = PdArray(pd_lines = [__id__, __xpos__, __ypos__, x.tag])
        obj.subclass = x.findtext('subclass')
        obj.name = x.findtext('name')
        obj.keep = x.findtext('keep') and x.findtext('keep') == "True"
        if x.tag == 'array': obj.size = x.findtext('size')
      
      # IEMGUI-group object
      elif x.tag in IEMGuiNames:
        obj = self.addIEMGui(x, __id__, __xpos__, __ypos__)
      
      else:
        # print('Making', x.tag)
        obj = PdObject(pd_lines=[
          __id__, __xpos__, __ypos__,
          self.__conv__.to_pd_obj(x.tag)
        ])

      # done with if statement, 
      # add the arguments to the object
      # and the object to the canvas
      self.addArgs(obj, x)
      if border: obj.border = border
      __last_canvas__.add(obj)


  def addArgs(self, obj, x):
    __args__ = x.find('arg')
    if __args__ is not None:
      for a in x.findall('arg'):
        # print("ARGS", a.text)
        obj.addargs([a.text])


  def addIEMGui(self, x, __id__, __xpos__, __ypos__):
    obj = PdIEMGui(pd_lines=[__id__, __xpos__, __ypos__, x.tag])

    tag = 'radio' if 'radio' in x.tag else x.tag

    __label__ = x.find('label')
    if __label__:
      label_params = [
        __label__.findtext('label', 
          default = self.__d__.iemgui['symbol']),
      ]

      __offset__ = __label__.find('offset')
      if __offset__:
        label_params += [
        __offset__.findtext('x', 
          default = self.__d__.iemgui[tag]['xoff']),
        __offset__.findtext('y', 
          default = self.__d__.iemgui[tag]['yoff'])
        ]
      else:
        label_params += [
          self.__d__.iemgui[tag]['xoff'],
          self.__d__.iemgui[tag]['yoff']
        ]

      __font__ = __label__.find('font')
      if __font__:
        label_params += [
        __font__.findtext('face', 
          default = self.__d__.iemgui['fontface']),
        __font__.findtext('size', 
          default = self.__d__.iemgui[tag]['fsize'])
        ]
      else:
        label_params += [
          self.__d__.iemgui['fontface'],
          self.__d__.iemgui[tag]['fsize']
        ]

      label_params += [
        __label__.findtext('lbcolor', 
          default = self.__d__.iemgui[tag]['lbcolor'])
      ]

    else:
      label_params = [
        self.__d__.iemgui['symbol'],
        self.__d__.iemgui[tag]['xoff'],
        self.__d__.iemgui[tag]['yoff'],
        self.__d__.iemgui['fontface'],
        self.__d__.iemgui[tag]['fsize'],
        self.__d__.iemgui[tag]['lbcolor']
      ]
    label_params += [
      self.__d__.iemgui[tag]['bgcolor'],
      self.__d__.iemgui['fgcolor'],
    ]
    # log(0,"TAG",x.tag)
    if 'vu' in x.tag:
      area_params, _ = self.getAreaAndLimits(x,'vu', get_limits=False)
      obj.createVu([
        area_params['width'],
        area_params['height'],
        x.findtext('receive', default = self.__d__.iemgui['symbol']), 
        *label_params, 
        x.findtext('scale', default = self.__d__.iemgui['vu']['scale']),
        x.findtext('flag',  default = self.__d__.iemgui['vu']['flag']),
      ])
    elif 'tgl' in x.tag:
      obj.createToggle([
        x.findtext('size', default = self.__d__.iemgui['tgl']['size']),
        x.findtext('init', default = self.__d__.iemgui['tgl']['init']),
        x.findtext('send', default = self.__d__.iemgui['symbol']), 
        x.findtext('receive', default = self.__d__.iemgui['symbol']), 
        *label_params, 
        x.findtext('flag', default = self.__d__.iemgui['tgl']['flag']),
        x.findtext('nonzero', default = self.__d__.iemgui['tgl']['nonzero']),
      ])
    elif 'cnv'  in x.tag  or 'my_canvas' in x.tag:
      area_params, _ = self.getAreaAndLimits(x, 'cnv', get_limits=False)
      obj.createCnv([
        x.findtext('size',    default = self.__d__.iemgui['cnv']['size']),
        area_params['width'],
        area_params['height'],
        x.findtext('send',    default = self.__d__.iemgui['symbol']), 
        x.findtext('receive', default = self.__d__.iemgui['symbol']), 
        *label_params, 
        x.findtext('flag', default = self.__d__.iemgui['cnv']['flag']),
      ])
    elif 'rdb'  in x.tag or 'radio' in x.tag:
      obj.createRadio([
        x.findtext('size',  default = self.__d__.iemgui['radio']['size']),
        x.findtext('flag',  default = self.__d__.iemgui['radio']['flag']),
        x.findtext('init',  default = self.__d__.iemgui['radio']['init']),
        x.findtext('number',default = self.__d__.iemgui['radio']['number']),
        x.findtext('send',  default = self.__d__.iemgui['symbol']), 
        x.findtext('receive',default = self.__d__.iemgui['symbol']), 
        *label_params, 
        x.findtext('value', default=self.__d__.iemgui['radio']['value']),
      ])
    elif 'bng' in x.tag:
      obj.createBng([
        x.findtext('size',   default = self.__d__.iemgui['bng']['size']),
        x.findtext('hold',   default = self.__d__.iemgui['bng']['hold']),
        x.findtext('intrrpt',default = self.__d__.iemgui['bng']['intrrpt']),
        x.findtext('init',   default = self.__d__.iemgui['bng']['init']),
        x.findtext('send',   default = self.__d__.iemgui['symbol']), 
        x.findtext('receive',default = self.__d__.iemgui['symbol']), 
        *label_params
      ])
    elif 'nbx' in x.tag:
      _, limits_params = self.getAreaAndLimits(x, 'nbx', get_area=False)
      obj.createNbx([
        x.findtext('digits_width', default=self.__d__.iemgui[x.tag]['digits_width']),
        x.findtext('height',  default = self.__d__.iemgui['nbx']['height']),
        limits_params['lower'],
        limits_params['upper'],
        x.findtext('log_flag',default = self.__d__.iemgui['nbx']['log_flag']),
        x.findtext('init',    default = self.__d__.iemgui['nbx']['init']),
        x.findtext('send',    default = self.__d__.iemgui['symbol']), 
        x.findtext('receive', default = self.__d__.iemgui['symbol']), 
        *label_params, 
        x.findtext('value',   default = self.__d__.iemgui['nbx']['value']), 
        x.findtext('log_height', default = self.__d__.iemgui['nbx']['log_height']), 
      ])
    elif 'vsl' in x.tag  or 'vslider' in x.tag:
      area_params, limits_params = self.getAreaAndLimits(x, 'vsl')
      obj.createSlider([
        area_params['width'],
        area_params['height'],
        limits_params['lower'],
        limits_params['upper'],
        x.findtext('log_flag',default = self.__d__.iemgui['vsl']['log_flag']),
        x.findtext('init',    default = self.__d__.iemgui['vsl']['init']),
        x.findtext('send',    default = self.__d__.iemgui['symbol']), 
        x.findtext('receive', default = self.__d__.iemgui['symbol']), 
        *label_params, 
        x.findtext('value',     default = self.__d__.iemgui['vsl']['value']), 
        x.findtext('log_height',default = self.__d__.iemgui['vsl']['log_height']), 
        x.findtext('steady',default = self.__d__.iemgui['vsl']['steady']), 
      ])
    elif 'hsl' in x.tag or 'hslider' in x.tag:
      area_params, limits_params = self.getAreaAndLimits(x, 'hsl')
      obj.createSlider([
        area_params['width'],
        area_params['height'],
        limits_params['lower'],
        limits_params['upper'],
        x.findtext('log_flag',default = self.__d__.iemgui['hsl']['log_flag']),
        x.findtext('init',    default = self.__d__.iemgui['hsl']['init']),
        x.findtext('send',    default = self.__d__.iemgui['symbol']), 
        x.findtext('receive', default = self.__d__.iemgui['symbol']), 
        *label_params, 
        x.findtext('value',     default = self.__d__.iemgui['hsl']['value']), 
        x.findtext('log_height',default = self.__d__.iemgui['hsl']['log_height']), 
        x.findtext('steady',default = self.__d__.iemgui['hsl']['steady']), 
      ])
    else:
      print('Unknown IEMGUI object type:', x.tag)
    
    # end iemgui if statement -----------------------------------------------
    # obj.dumps()

    return obj

  def getAreaAndLimits(self, x, className, get_limits=True, get_area=True):
    area_params = None
    limits_params = None
    
    if get_area:
      area = x.find('area')
      if area is not None:
        area_params = {
          'width' : area.findtext('width',   default = self.__d__.iemgui[className]['width']),
          'height': area.findtext('height',  default = self.__d__.iemgui[className]['height']),
        }
      else:
        area_params = {
          'width' : self.__d__.iemgui[className]['width'],
          'height': self.__d__.iemgui[className]['height'],
        }
    
    if get_limits:
      limits = x.find('limits')
      if limits is not None:
        limits_params = {
          'lower': limits.findtext('lower',   default = self.__d__.iemgui[className]['lower']),
          'upper': limits.findtext('upper',   default = self.__d__.iemgui[className]['upper']),
        }
      else:
        limits_params = {
          'lower': self.__d__.iemgui[className]['lower'],
          'upper': self.__d__.iemgui[className]['upper'],
        }
    return area_params, limits_params
  # end of addIEMGui definition ---------------------------------------------
