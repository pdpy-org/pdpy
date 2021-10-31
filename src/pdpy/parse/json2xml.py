#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Json-formatted file (Python Patch Object) to XML file """

from pdpy.parse.getters import get
from ..util.utils import log
# from ..classes.classes import GOPArrayFlags

import xml.etree.ElementTree as ET

__all__ = [ "JsonToXml" ]

class JsonToXml:
  
  def __init__(self, obj, autoindent=True):

    # do not continue loading if root is not present
    if not hasattr(obj, "root"):
      return

    # The json as python object
    self.obj = obj
    self.root = getattr(obj, 'root')

    # This is a list that holds the self.depth of the current object
    self.depth = []

    # This is a dictionary with 
    # - the node indices as keys, and 
    # - the last self.depth index as values
    self.obj_map = {}

    self.__root__ = ET.Element('patch', attrib={'name': self.obj.patchname})
    self.tree = ET.ElementTree(self.__root__)

    # add main root canvas
    cnv = self.getCanvas(self.root, self.__root__, root=True)
    # add structs
    self.getStruct(self.obj, cnv)
    # add declarations
    self.getDependencies(self.obj, cnv)
    # add nodes
    self.getNodes(self.root, cnv)
    # add comments
    self.getComments(self.root, cnv)
    # add coords
    self.getCoords(self.root, cnv)
    # add connections
    self.getConnections(self.root, cnv)
    # add restore (if gop)
    self.getRestore(self.root, cnv)
    
    if autoindent:
      ET.indent(self.tree, space=' ', level=1)

  def to_string(self):
    return ET.tostring(self.__root__, encoding='unicode', method='xml')

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


  def get(self, x, prop, subprop=None, default=None):

    if isinstance(x, dict) or isinstance(x, list):
      o = x[prop]
    else:
      o = getattr(x, str(prop))
    
    if subprop is None:
      if o is not None:
        if isinstance(o, list):
          return o
        else:
          return str(o)
      else:
        return default
    else:
      return self.get(o, subprop)

  # **************************************************************************** #
  # Routines to get data from structured pdpy json file into pd-formatted string
  # **************************************************************************** #

  def getStruct(self, x, cnv):
    if hasattr(x, 'struct'):
      for d in getattr(x,'struct'):
        struct = ET.SubElement(cnv, 'struct')
        self.update_with_sub(d, 'name', struct)
        self.update_with_sub(d, 'float', struct)
        self.update_with_sub(d, 'symbol', struct)
        self.update_with_sub(d, 'text', struct)
        if hasattr(d, 'array'):
          for x in self.get(d,'array'):
            array = ET.SubElement(struct, 'array')
            self.update_with_sub(x, 'name', array)
            self.update_with_sub(x, 'template', array)

  def getComments(self, x, cnv):
    if hasattr(x, 'comments'):
      for x in self.get(x,'comments'):
        comment = ET.SubElement(cnv, 'comment')
        comment.text = ' '.join(getattr(x,'text'))
        position = getattr(x, 'position')
        self.update_with_sub(position, 'x', comment)
        self.update_with_sub(position, 'y', comment)
        self.update_with_sub(x, 'border', comment)

  def getConnections(self, x, cnv):
    if hasattr(x, 'edges'):
      for x in self.get(x,'edges'):
        connect = ET.SubElement(cnv, 'connect')
        source = ET.SubElement(connect, 'source')
        sink = ET.SubElement(connect, 'sink')
        src = getattr(x, 'source')
        snk = getattr(x, 'sink')
        self.update_with_sub(src, 'id', source)
        self.update_with_sub(src, 'port', source)
        self.update_with_sub(snk, 'id', sink)
        self.update_with_sub(snk, 'port', sink)

  def getNodes(self, x, cnv):
    if hasattr(x, 'nodes'):
      for node in getattr(x, 'nodes'):
        if hasattr(node, 'nodes'):
          # a canvas, recurse
          self.getCanvas(node, cnv, root=False)
          continue

        if hasattr(node, 'className'):
          className = self.to_xml_tag(getattr(node,'className'))
        else:
          className = 'obj'
        
        objid = { 'id': str(getattr(node,'id')) }
        
        e = ET.Element(className, attrib=objid)
        cnv.append(e)

        if hasattr(node, 'position'):
          position = getattr(node,'position')
          self.update_with_sub(position, 'x', e)
          self.update_with_sub(position, 'y', e)

        if hasattr(node, "targets"):
          for t in getattr(node,'targets'):
            target = ET.SubElement(e, 'target')
            target.text = getattr(t, 'address')
            for m in getattr(t,'message'):
              ET.SubElement(target, 'message').text = str(m)

        for i in ['receive','send','bgcolor','fgcolor','scale','flag','size','init','nonzero','number','value','hold','intrrpt','digit_width','height', 'log_flag', 'log_height', 'steady', 'subclass', 'name', 'keep']:
          self.update_with_sub(node, i, e)

        if hasattr(node,'label'):
          label = ET.SubElement(e, 'label')
          label.text = str(getattr(node,'label'))
          if hasattr(node,'offset'):
            off = getattr(node,'offset')
            self.update_with_sub(off, 'x', label)
            self.update_with_sub(off, 'y', label)
          if hasattr(node,'font'):
            font = getattr(node,'font')
            self.update_with_sub(font, 'size', label)
            self.update_with_sub(font, 'face', label)
          self.update_with_sub(node, 'lbcolor', label)

        if hasattr(node,'area'):
          a = getattr(node,'area')
          area = ET.SubElement(e, 'area')
          self.update_with_sub(a, 'width', area)
          self.update_with_sub(a, 'height', area)

        if hasattr(node, 'limits'):
          lim = getattr(node, 'limits')
          limits = ET.SubElement(e, 'limits')
          self.update_with_sub(lim, 'lower', limits)
          self.update_with_sub(lim, 'upper', limits)

        if hasattr(node, 'data'):
          data = ET.SubElement(e, 'data')
          for d in self.get(node,'data'):
            if isinstance(d, str):
              ET.SubElement(data, 'symbol').text = d
            elif isinstance(e, list):
              array = ET.SubElement(data, 'array')
              for l in d:
                ET.SubElement(array, 'float').text = str(l)
            else:
              ET.SubElement(data, 'float').text = str(d)
          
        if hasattr(node,'args'):
          args = self.get(node,'args')
          if not isinstance(args, list):
            args = [args]
          for arg in args:
            ET.SubElement(e, 'arg').text = arg
      
      self.update_with_sub(x, 'border', e)

  def getDeclare(self, kind):
    if hasattr(self.root, kind):
      declares = ET.SubElement(self.__root__, 'declare')
      for x in self.get(self.root, kind):
        ET.SubElement(declares, kind[:-1]).text = x
      

  def getDependencies(self, x, cnv):
    """ Parses the dependencies entry into paths and libs using `getDeclare()` """
    if hasattr(x, "dependencies"):
      self.getDeclare(self.get(cnv,'dependencies'), 'paths')
      self.getDeclare(self.get(cnv,'dependencies'), 'libs')

  def getRestore(self, x, cnv):
    # Get the self.depth and remove the last element
    
    self.depth.pop()
    
    if hasattr(x, 'position'):
      position = getattr(x, 'position')
      self.update_with_sub(position, 'x', cnv)
      self.update_with_sub(position, 'y', cnv)
      self.update_with_sub(x, 'title', cnv)

  # def getBorder(self, x, cnv):
    # if hasattr(x, 'border'):
      # ET.SubElement(cnv, 'border').text = self.get(x,'border')

  def getCoords(self, x, cnv):
    if hasattr(x, 'coords'):
      coords = ET.SubElement(cnv, 'coords')

      a = ET.SubElement(coords, 'a')
      b = ET.SubElement(coords, 'b')
      ET.SubElement(a, 'xpos').text = self.get(self.get(x,'coords','range'),'a','x')
      ET.SubElement(b, 'xpos').text = self.get(self.get(x,'coords','range'),'b','x')
      ET.SubElement(a, 'ypos').text = self.get(self.get(x,'coords','range'),'a','y')
      ET.SubElement(b, 'xpos').text = self.get(self.get(x,'coords','range'),'b','y')

      ET.SubElement(coords, 'width').text = self.get(self.get(x,'coords','dimension'),'width')
      ET.SubElement(coords, 'height').text = self.get(self.get(x,'coords','dimension'),'height')
      
      ET.SubElement(coords, 'gop').text = self.get(x,'coords','gop')
      
      if hasattr(self.get(x,'coords'), 'margin'):
        mgn = ET.SubElement(coords, 'margin')
        ET.SubElement(mgn, 'x').text = self.get(self.get(x,'coords','margin'),'x')
        ET.SubElement(mgn, 'y').text = self.get(self.get(x,'coords','margin'),'y')
      

  def getCanvas(self, x, canvas, root=False):
    """ Fill in the canvas element 
    
    Description
    -----------
    This function is called recursively to fill in the canvas element.

    The x argument is the current json object being processed.
    It must have a canvas type object.


    """

    # Get the self.depth and add a new element with -1
    
    self.depth.append(-1)
    
    cnv = ET.Element('canvas')
    canvas.append(cnv)

    if hasattr(x, 'screen'):
      screen = getattr(x, 'screen')
      self.update_with_sub(screen, 'x', cnv)
      self.update_with_sub(screen, 'y', cnv)

    if hasattr(x, 'dimension'):
      dimen = getattr(x, 'dimension')
      self.update_with_sub(dimen, 'width', cnv)
      self.update_with_sub(dimen, 'height', cnv)

    # Do not add name and vis flag if it is the root, add font instead
    if root:
      self.update_with_sub(x, 'font', cnv)
      return cnv
    else:
      self.update_with_sub(x, 'name', cnv)
      self.update_with_sub(x, 'vis', cnv)
      # recurse through the nodes if it is not the root

    if not root:
      self.getNodes(x, cnv)
      self.getComments(x, cnv)
      self.getConnections(x, cnv)
      self.getCoords(x, cnv)
      self.getRestore(x, cnv)
      self.update_with_sub(x, 'border', cnv)

  def update_with_sub(self, x, attribute, parent):
    """ Updates the attribute of the parent with the object's attribute """
    if hasattr(x, attribute):
      ET.SubElement(parent, attribute).text = str(getattr(x, attribute))


  def to_xml_tag(self, tag):
    """ Returns the tag name replacing special characters """
    
    tag = tag.replace('~','_tilde')
    
    tag = tag.replace('%','op_mod')
    tag = tag.replace('*','op_mul')
    tag = tag.replace('-','op_minus')
    tag = tag.replace('+','op_plus')
    tag = tag.replace('/','op_div')

    tag = tag.replace('==','op_eq')
    tag = tag.replace('!=','op_ne')
    tag = tag.replace('>','op_gt')
    tag = tag.replace('<','op_lt')
    tag = tag.replace('>=','op_ge')
    tag = tag.replace('<=','op_le')
    
    tag = tag.replace('||','op_or')
    tag = tag.replace('&&','op_and')
    tag = tag.replace('!','op_not')
    
    tag = tag.replace('&','binop_and')
    tag = tag.replace('|','binop_bor')
    tag = tag.replace('>>','binop_ls')
    tag = tag.replace('<<','binop_rs')
    
    return tag