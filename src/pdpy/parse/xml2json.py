#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Convert an XML file to a JSON structured file (PdPy format) """

import xml.etree.ElementTree as ET
from ..classes.iemgui import IEMLabel, PdIEMGui
from ..classes.pdpy import PdPy
from ..classes.default import Default, IEMGuiNames, XmlTagConvert
from ..classes.canvas import Canvas
from ..classes.classes import Comment, Edge, PdArray, PdMessage, PdNativeGui, PdObject
# from ..util.utils import log

__all__ = [ "XmlToJson" ]

class XmlToJson:
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
    self.patch.root = Canvas(
      name = self.patch.patchname,
      vis = self.__x__.findtext('vis', default=self.__d__.vis),
      screen = [
        self.__x__.findtext('x', default=self.__d__.screen['x']), 
        self.__x__.findtext('y', default=self.__d__.screen['x'])
      ],
      dimen  = [
        self.__x__.findtext('width', default=self.__d__.dimen['width']),
        self.__x__.findtext('height',default=self.__d__.dimen['height'])
      ],
      font=self.__x__.findtext('font', default=self.__d__.font['size'])
    )

    for child in self.__x__.findall('*'):
      # getStruct(o, out)
      # # add main root canvas
      # getCanvas(o.root, out, root=True)
      # # add declarations
      # getDependencies(o, out)
      # # add nodes
      # getNodes(o.root, out)
      # # add comments
      # getComments(o.root, out)
      # # add coords
      # getCoords(o.root, out)
      # # add connections
      # getConnections(o.root, out)
      # # add restore (if gop)
      # getRestore(o.root, out)
      self.addNodes(child, self.patch.root)
      self.addComments(child, self.patch.root)
      self.addConnections(child, self.patch.root)

  def addComments(self, x, __last_canvas__):
    if 'comment' == x.tag:
      __last_canvas__.comment(
      Comment(
        x.findtext('x'), 
        x.findtext('y'),
        x.text)
      )
      return

  def addConnections(self, x, __last_canvas__):
    if 'connect' == x.tag:
      __last_canvas__.edge(
        Edge( 
          x.find('source').findtext('id'),
          x.find('source').findtext('port'),
          x.find('sink').findtext('id'),
          x.find('sink').findtext('port'))
        )

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
      self.addNodes(child, canvas)
      self.addComments(child, canvas)
      self.addConnections(child, canvas)


  def addNodes(self, x, __last_canvas__):
    if x.tag in ['vis', 'x', 'y', 'width', 'height', 'font', 'title', 'name', 'connect', 'comment']:
      return
    elif 'canvas' == x.tag:
      self.addCanvas(x)
      return
    else:  
      self.patch.__obj_idx__ = __last_canvas__.grow()
      print(x)
      __id__   = int(x.get('id', default = self.patch.__obj_idx__ ))
      __xpos__ = int(x.findtext('x'))
      __ypos__ = int(x.findtext('y'))
      
      if 'msg' == x.tag:
        msg = PdMessage(__id__, __xpos__, __ypos__)
        for t in x.findall('target'):
          msg.addTarget(t.text)
          for m in t.findall('message'):
            msg.targets[-1].add(m.text)
        
        __last_canvas__.add(msg)
        return
      
      if x.tag in ['floatatom', 'symbolatom', 'listbox']:
        # print( "Make PdNativeGui", x.tag)
        obj = PdNativeGui(
          x.tag, __id__, __xpos__, __ypos__,
          x.findtext('digits_width', default=self.__d__.digits_width),
          x.findtext('lower', default=self.__d__.limits['lower']),
          x.findtext('upper', default=self.__d__.limits['upper']),
          x.findtext('flag', default=self.__d__.flag),
          x.findtext('label', default=self.__d__.label),
          x.findtext('receive', default=self.__d__.receive),
          x.findtext('send', default=self.__d__.send))
        __last_canvas__.add(obj)
        return
      
      # text or array-group objects
      if "text" == x.tag or 'array' == x.tag:
        __subclass__ = x.findtext('subclass')
        __name__     = x.findtext('name')
        __keep__ = x.findtext('keep') and x.findtext('keep') == "True"
        if x.tag == 'array':
          __size__ = self.__d__.array['size']
          if x.findtext('size'):
            __size__ = x.findtext('size')
          obj = PdArray(
            __id__, __xpos__, __ypos__, x.tag,
            __subclass__, __name__, __keep__, __size__
          )
        else:
          obj = PdArray(
            __id__, __xpos__, __ypos__, x.tag,
            __subclass__, __name__, __keep__
          )
        for a in x.findall('arg'):
          obj.addargs(a.text)

        __last_canvas__.add(obj)
        return
      
      # IEMGUI-group object
      elif x.tag in IEMGuiNames:
        obj = PdIEMGui(__id__, __xpos__, __ypos__)
        __label__ = x.find('label')
        label = IEMLabel(
          __label__.findtext('label', 
            default = self.__d__.iemgui['symbol']),
          __label__.find('offset').findtext('x', 
            default = self.__d__.iemgui[x.tag]['xoff']),
          __label__.find('offset').findtext('y', 
            default = self.__d__.iemgui[x.tag]['yoff']),
          __label__.find('font').findtext('face', 
            default = self.__d__.iemgui['fontface']),
          __label__.find('font').findtext('size', 
            default = self.__d__.iemgui[x.tag]['font']),
          __label__.findtext('lbcolor', 
            default = self.__d__.iemgui[x.tag]['label']['color']),
        )
        label_params = [  
          label.label,
          label.offset.x,
          label.offset.y,
          label.font.face,
          label.font.size,
          label.lbcolor
        ]
        
        if 'vu' in x.tag:
          obj.createVu(
            x.findtext('width',   default = self.__d__.iemgui[x.tag]['width']),
            x.findtext('height',  default = self.__d__.iemgui[x.tag]['height']),
            x.findtext('receive', default = self.__d__.iemgui[x.tag]['receive']), 
            *label_params, 
            x.findtext('scale', default = self.__d__.iemgui[x.tag]['scale']),
            x.findtext('flag',  default = self.__d__.iemgui[x.tag]['flag']),
          )
        elif 'tgl' in x.tag:
          obj.createToggle(
            x.findtext('size', default = self.__d__.iemgui[x.tag]['size']),
            x.findtext('init', default = self.__d__.iemgui[x.tag]['init']),
            x.findtext('send', default = self.__d__.iemgui[x.tag]['send']), 
            x.findtext('receive', default = self.__d__.iemgui[x.tag]['receive']), 
            *label_params, 
            x.findtext('flag', default = self.__d__.iemgui[x.tag]['flag']),
            x.findtext('nonzero', default = self.__d__.iemgui[x.tag]['nonzero']),
          )
        elif 'cnv' in x.tag:
          obj.createCnv(
            x.findtext('size',    default = self.__d__.iemgui[x.tag]['size']),
            x.findtext('width',   default = self.__d__.iemgui[x.tag]['width']),
            x.findtext('height',  default = self.__d__.iemgui[x.tag]['height']),
            x.findtext('send',    default = self.__d__.iemgui[x.tag]['send']), 
            x.findtext('receive', default = self.__d__.iemgui[x.tag]['receive']), 
            *label_params, 
            x.findtext('flag', default = self.__d__.iemgui[x.tag]['flag']),
          )
        elif 'radio' in x.tag:
          obj.createRadio(
            x.findtext('size',    default = self.__d__.iemgui[x.tag]['size']),
            x.findtext('flag',    default = self.__d__.iemgui[x.tag]['flag']),
            x.findtext('init',    default = self.__d__.iemgui[x.tag]['init']),
            x.findtext('number',  default = self.__d__.iemgui[x.tag]['number']),
            x.findtext('send',    default = self.__d__.iemgui[x.tag]['send']), 
            x.findtext('receive', default = self.__d__.iemgui[x.tag]['receive']), 
            *label_params, 
            x.findtext('value', default=self.__d__.iemgui[x.tag]['value']),
          )
        elif 'bng' in x.tag:
          obj.createBng(
            x.findtext('size',    default = self.__d__.iemgui[x.tag]['size']),
            x.findtext('hold',    default = self.__d__.iemgui[x.tag]['hold']),
            x.findtext('intrrpt', default = self.__d__.iemgui[x.tag]['intrrpt']),
            x.findtext('init',    default = self.__d__.iemgui[x.tag]['init']),
            x.findtext('send',    default = self.__d__.iemgui[x.tag]['send']), 
            x.findtext('receive', default = self.__d__.iemgui[x.tag]['receive']), 
            *label_params
          )
        elif 'nbx' in x.tag:
          obj.createNbx(
            x.findtext('digits_width', default=self.__d__.iemgui[x.tag]['digits_width']),
            x.findtext('height',  default = self.__d__.iemgui[x.tag]['height']),
            x.findtext('lower',   default = self.__d__.iemgui[x.tag]['lower']),
            x.findtext('upper',   default = self.__d__.iemgui[x.tag]['upper']),
            x.findtext('log_flag',default = self.__d__.iemgui[x.tag]['log_flag']),
            x.findtext('init',    default = self.__d__.iemgui[x.tag]['init']),
            x.findtext('send',    default = self.__d__.iemgui[x.tag]['send']), 
            x.findtext('receive', default = self.__d__.iemgui[x.tag]['receive']), 
            *label_params, 
            x.findtext('value',   default = self.__d__.iemgui[x.tag]['value']), 
            x.findtext('log_height', default = self.__d__.iemgui[x.tag]['log_height']), 
          )
        elif 'sl' in x.tag:
          obj.createSlider(
            x.findtext('width',   default = self.__d__.iemgui[x.tag]['width']),
            x.findtext('height',  default = self.__d__.iemgui[x.tag]['height']),
            x.findtext('lower',   default = self.__d__.iemgui[x.tag]['lower']),
            x.findtext('upper',   default = self.__d__.iemgui[x.tag]['upper']),
            x.findtext('log_flag',default = self.__d__.iemgui[x.tag]['log_flag']),
            x.findtext('init',    default = self.__d__.iemgui[x.tag]['init']),
            x.findtext('send',    default = self.__d__.iemgui[x.tag]['send']), 
            x.findtext('receive', default = self.__d__.iemgui[x.tag]['receive']), 
            *label_params, 
            x.findtext('value',     default = self.__d__.iemgui[x.tag]['value']), 
            x.findtext('log_height',default = self.__d__.iemgui[x.tag]['log_height']), 
          )
        else:
          print('Unknown IEMGUI object type:', x.tag)
        
      # end iemgui if statement -----------------------------------------------
      
      else:
        print('Making', x.tag)
        obj = PdObject(__id__,__xpos__,__ypos__,self.__conv__.to_pd_obj(x.tag))

      for a in x.findall('arg'):
        print("args", a.text)
        obj.addargs([a.text])

      __last_canvas__.add(obj)
