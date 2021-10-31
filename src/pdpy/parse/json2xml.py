#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Json-formatted file (Python Patch Object) to XML file """

from ..util.utils import log
# from ..classes.classes import GOPArrayFlags

import xml.etree.ElementTree as ET

__all__ = [ "JsonToXml" ]

class JsonToXml:
  
  def __init__(self, obj):

    # do not continue loading if root is not present
    if not hasattr(obj, "root"):
      return

    # The json as python object
    self.obj = obj

    # This is a list that holds the self.depth of the current object
    self.depth = []

    # This is a dictionary with 
    # - the node indices as keys, and 
    # - the last self.depth index as values
    self.obj_map = {}

    self.et = ET.ElementTree('patch', attributes={'name':self.obj.patchname})

    # add structs
    self.getStruct()
    # add main root canvas
    self.getCanvas(self.obj, root=True)
    # add declarations
    self.getDependencies()
    # add nodes
    self.getNodes()
    # add comments
    self.getComments()
    # add coords
    self.getCoords()
    # add connections
    self.getConnections()
    # add restore (if gop)
    self.getRestore()


  def __map_idx__(self, id):
    """ Maps a node id to a unique index """
    # increment the last self.depth index by one
    self.depth[-1] += 1
    # add the node to the map
    self.obj_map.update({ id : self.depth[-1] })

  def __remap__(self, id):
    """ Get the value from the mapped indices """
    # get the object map
    
    s = '-1'
    try:
      # query the map for the value at the id key
      s = str( self.obj_map[int(id)] )
    except KeyError:
      # if the key is not found, log the error
      log(1, "__remap__()::Key Not Found", id)
      print(self.obj_map)
    finally:
      # return the value
      return s


  def get(self, prop, subprop=None, default=None):

    if isinstance(self.obj, dict) or isinstance(self.obj, list):
      o = self.obj[prop]
    else:
      o = getattr(self.obj, str(prop))
    
    if subprop is None:
      return o if o is not None else default
    else:
      return self.get(o, subprop)

  # **************************************************************************** #
  # Routines to get data from structured pdpy json file into pd-formatted string
  # **************************************************************************** #

  def getStruct(self):
    """ Parses the struct entry into pd-lingo 
    
    Description
    -----------  
      This function takes a python object `obj` (coming from json),
      and an `out` list. 
    
    It returns `None`, but they append pd-formatted strings to the `out` list
    
    """
    if hasattr(self.obj, 'struct'):
      for d in self.get(self,'struct'):
        struct = ET.SubElement(self.et, 'struct')
        ET.SubElement(struct, 'name').text = self.get(d,'name')

        if hasattr(d, 'float'):
          ET.SubElement(struct, 'float').text = self.get(d,'float')
        
        if hasattr(d, 'symbol'):
          ET.SubElement(struct, 'symbol').text = self.get(d,'symbol')
        
        if hasattr(d, 'text'):
          ET.SubElement(struct, 'text').text = self.get(d,'text')
        
        if hasattr(d, 'array'):
          for x in self.get(d,'array'):
            array = ET.SubElement(struct, 'array')
            ET.SubElement(array, 'name').text = self.get(x,'name')
            ET.SubElement(array, 'template').text = self.get(x,'template')
        
        

  def getComments(self):
    if hasattr(self.obj, 'comments'):
      for x in self.get(self.obj,'comments'):
        comment = ET.SubElement(self.et, 'comment')
 
        ET.SubElement(comment, 'xpos').text = self.get(x,'position','x')
        ET.SubElement(comment, 'ypos').text = self.get(x,'position','y')

        if len(self.get(x,'text')) == 1: 
          comment.text = self.get(x, 'text', 0)
        else: 
          comment.text = ' '.join([ f"{t} \\;" for t in self.get(x,'text') ])
        
        if hasattr(x, 'border'): 
          ET.SubElement(comment, 'xpos').text = self.get(x,'border')
        

  def getConnections(self):
    if hasattr(self.obj, 'edges'):
      for x in self.get(self.obj,'edges'):
        connect = ET.SubElement(self.et, 'connect')
        source = ET.SubElement(connect, 'source')
        sink = ET.SubElement(connect, 'sink')

        ET.SubElement(source, 'id').text = self.__remap__(self.get(x,'source','id'))
        ET.SubElement(source, 'port').text = self.get(x,'source','port')
        ET.SubElement(sink, 'id').text = self.__remap__(self.get(x,'sink','id'))
        ET.SubElement(sink, 'port').text = self.get(x,'sink','port')

  def getNodes(self):
    if hasattr(self.obj, 'nodes'):
      for x in self.obj.nodes:

        if hasattr(x, 'nodes'):
          # a canvas, recurse
          self.getCanvas(x)
          continue

        if hasattr(x, 'className'):
          className = self.get(x,'className')
        else:
          className = 'obj'

        e = ET.SubElement(self.et, className, attrib={'id':self.get(x,'id')})

        if hasattr(x, 'xpos'):
          ET.SubElement(e, 'xpos').text = self.get(x,'position','x')
        if hasattr(x, 'ypos'):
          ET.SubElement(e, 'ypos').text = self.get(x,'position','y')

        if hasattr(x, "targets"):
          for t in self.get(x,'targets'):
            target = ET.SubElement(e, 'target')
            target.text = self.get(t,'address')
            for m in self.get(t,'message'):
              ET.SubElement(target, 'message').text = m

        if hasattr(x,'receive'):
          ET.SubElement(e, 'receive').text = self.get(x,'receive')

        if hasattr(x,'send'):
          ET.SubElement(e, 'send').text = self.get(x,'send')

        if hasattr(x,'label'):
          label = ET.SubElement(e, 'label')
          label.text = self.get(x,'label')
          if hasattr(x,'offset'):
            ET.SubElement(label, 'xoff').text = self.get(x,'offset', 'x')
            ET.SubElement(label, 'yoff').text = self.get(x,'offset', 'y')
          if hasattr(x,'font'):
            ET.SubElement(label, 'fsize').text = self.get(x,'font', 'size')
            ET.SubElement(label, 'fface').text = self.get(x,'font', 'face')
          if hasattr(x,'lbcolor'):
            ET.SubElement(label, 'color').text = self.get(x,'lbcolor')

        if hasattr(x,'bgcolor'):
          ET.SubElement(label, 'bgcolor').text = self.get(x,'bgcolor')

        if hasattr(x,'fgcolor'):
          ET.SubElement(label, 'fgcolor').text = self.get(x,'fgcolor')

        if hasattr(x,'area'):
          area = ET.SubElement(e, 'area')
          # fill out the area attributes width width and height
          ET.SubElement(area, 'width').text = self.get(x,'area','width')
          ET.SubElement(area, 'height').text = self.get(x,'area','height')

        if hasattr(x,'scale'):
          ET.SubElement(e, 'scale').text = self.get(x,'scale')

        if hasattr(x,'flag'):
          ET.SubElement(e, 'flag').text = self.get(x,'flag')
        
        if hasattr(x,'size'):
          ET.SubElement(e, 'size').text = self.get(x,'size')

        if hasattr(x,'init'):
          ET.SubElement(e, 'init').text = self.get(x,'size')

        if hasattr(x, 'nonzero'):
          ET.SubElement(e, 'nonzero').text = self.get(x,'nonzero')

        if hasattr(x, 'number'):
          ET.SubElement(e, 'number').text = self.get(x,'number')
        
        if hasattr(x, 'value'):
          ET.SubElement(e, 'value').text = self.get(x,'value')
        
        if hasattr(x, 'hold'):
          ET.SubElement(e, 'hold').text = self.get(x,'hold')
        
        if hasattr(x, 'intrrpt'):
          ET.SubElement(e, 'intrrpt').text = self.get(x,'intrrpt')
        
        if hasattr(x, 'digit_width'):
          ET.SubElement(e, 'digit_width').text = self.get(x,'digit_width')
        
        if hasattr(x, 'height'):
          ET.SubElement(e, 'height').text = self.get(x,'height')
        
        if hasattr(x, 'limits'):
          limits = ET.SubElement(e, 'limits')
          ET.SubElement(limits, 'lower').text = self.get(x,'limits','lower')
          ET.SubElement(limits, 'upper').text = self.get(x,'limits','upper')
        
        if hasattr(x, 'log_flag'):
          ET.SubElement(e, 'log_flag').text = self.get(x,'log_flag')

        if hasattr(x, 'log_height'):
          ET.SubElement(e, 'log_height').text = self.get(x,'log_height')

        if hasattr(x, 'steady'):
          ET.SubElement(e, 'steady').text = self.get(x,'steady')

        if hasattr(x, "subclass"):
          ET.SubElement(e, 'subclass').text = self.get(x,'subclass')
        
        if hasattr(x, "keep") and self.get(x,'keep'):
          ET.SubElement(e, 'keep').text = self.get(x,'keep')

        if hasattr(x, "name"):
          ET.SubElement(e, 'name').text = self.get(x,'name')

        if hasattr(x, "data"):
          data = ET.SubElement(e, 'data')
          for d in self.get(x,'data'):
            if isinstance(d, str):
              ET.SubElement(data, 'symbol').text = d
            elif isinstance(e, list):
              array = ET.SubElement(data, 'array')
              for l in d:
                ET.SubElement(array, 'float').text = l
            else:
              ET.SubElement(data, 'float').text = d
          
        if hasattr(x,"args"):
          for arg in [ self.get(x,'args') ]:
            ET.SubElement(e, 'arg').text = arg
      
      self.getBorder(x, e)



  def getDeclare(self, kind):
    if hasattr(self.obj, kind):
      declares = ET.SubElement(self.et, 'declare')
      for x in self.get(self.obj, kind):
        ET.SubElement(declares, kind[:-1]).text = x
      

  def getDependencies(self):
    """ Parses the dependencies entry into paths and libs using `getDeclare()` """
    if hasattr(self.obj, "dependencies"):
      self.getDeclare(self.get(self.obj,'dependencies'), 'paths')
      self.getDeclare(self.get(self.obj,'dependencies'), 'libs')

  def getRestore(self):
    # Get the self.depth and remove the last element
    
    self.depth.pop()
    
    if hasattr(self.obj, 'position'):
      ET.SubElement(self.et, 'xpos').text = self.get(self.obj,'position','x')
      ET.SubElement(self.et, 'ypos').text = self.get(self.obj,'position','y')
      ET.SubElement(self.et, 'title').text = self.get(self.obj,'title')
      

  def getBorder(self, x, parent):
    if hasattr(x, 'border'):
      ET.SubElement(parent, 'border').text = self.get(x,'border')

  def getCoords(self):
    if hasattr(self.obj, 'coords'):
      coords = ET.SubElement(self.et, 'coords')

      a = ET.SubElement(coords, 'a')
      b = ET.SubElement(coords, 'b')
      ET.SubElement(a, 'xpos').text = self.get(self.get(self.obj,'coords','range'),'a','x')
      ET.SubElement(b, 'xpos').text = self.get(self.get(self.obj,'coords','range'),'b','x')
      ET.SubElement(a, 'ypos').text = self.get(self.get(self.obj,'coords','range'),'a','y')
      ET.SubElement(b, 'xpos').text = self.get(self.get(self.obj,'coords','range'),'b','y')

      ET.SubElement(coords, 'width').text = self.get(self.get(self.obj,'coords','dimension'),'width')
      ET.SubElement(coords, 'height').text = self.get(self.get(self.obj,'coords','dimension'),'height')
      
      ET.SubElement(coords, 'gop').text = self.get(self.obj,'coords','gop')
      
      if hasattr(self.get(self.obj,'coords'), 'margin'):
        mgn = ET.SubElement(coords, 'margin')
        ET.SubElement(mgn, 'x').text = self.get(self.get(self.obj,'coords','margin'),'x')
        ET.SubElement(mgn, 'y').text = self.get(self.get(self.obj,'coords','margin'),'y')
      

  def getCanvas(self, x, root=False):
    # Get the self.depth and add a new element with -1
    
    self.depth.append(-1)
    
    cnv = ET.SubElement(self.et, 'canvas')
    ET.SubElement(cnv, 'xpos').text = self.get(x,'screen','x')
    ET.SubElement(cnv, 'ypos').text = self.get(x,'screen','y')
    ET.SubElement(cnv, 'width').text = self.get(x,'dimension','width')
    ET.SubElement(cnv, 'height').text = self.get(x,'dimension','height')
    # Do not add name and vis flag if it is the root, add font instead
    if root:
      ET.SubElement(cnv, 'font').text = str(self.get(x,'font'))
    else:
      ET.SubElement(cnv, 'name').text = self.get(x,'name')
      ET.SubElement(cnv, 'vis').text = 1 if self.get(x,'vis') else 0
    
    # recurse through the nodes if it is not the root
    if not root:
      self.getNodes()
      self.getComments()
      self.getConnections()
      self.getCoords()
      self.getRestore()
      self.getBorder(x, cnv)
