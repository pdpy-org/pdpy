#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Json-formatted file (Python Patch Object) to XML file """

from ..util.utils import log
from ..classes.default import XmlTagConvert
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
    self.__conv__ = XmlTagConvert()
    # This is a list that holds the self.depth of the current object
    self.depth = []

    # This is a dictionary with 
    # - the node indices as keys, and 
    # - the last self.depth index as values
    self.obj_map = {}

    self.__root__ = ET.Element('patch', attrib={'name': self.obj.patchname})
    self.tree = ET.ElementTree(self.__root__)

    # add structs
    self.getStruct(self.obj, self.__root__)
    # add declarations
    self.getDependencies(self.obj)
    # add main root canvas
    cnv = self.getCanvas(self.root, self.__root__, root=True)
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
      ET.indent(self.tree, space='    ', level=0)

  def to_string(self):
    return ET.tostring(self.__root__, encoding='unicode', method='xml')

  def getStruct(self, x, root):
    if hasattr(x, 'struct'):
      struct = ET.SubElement(root, 'struct')
      for d in getattr(x,'struct'):
        template = ET.SubElement(struct, 'template')
        self.update_with_sub(d, 'name', template)
        self.update_with_sub(d, 'text', template)
        if hasattr(d, 'array'):
          for x in getattr(d,'array'):
            array = ET.SubElement(template, 'array')
            self.update_with_sub(x, 'name', array)
            self.update_with_sub(x, 'template', array)
        if hasattr(d, 'float'):
          for x in getattr(d,'float'):
            float = ET.SubElement(template, 'float')
            float.text = x
        if hasattr(d, 'symbol'):
          for x in getattr(d,'symbol'):
            symbol = ET.SubElement(template, 'symbol')
            symbol.text = x
  

  def getComments(self, x, cnv):
    if hasattr(x, 'comments'):
      for x in getattr(x,'comments'):
        comment = ET.SubElement(cnv, 'comment')
        comment.text = ' '.join(getattr(x,'text'))
        position = getattr(x, 'position')
        self.update_with_sub(position, 'x', comment)
        self.update_with_sub(position, 'y', comment)
        self.update_with_sub(x, 'border', comment)

  def getConnections(self, x, cnv):
    if hasattr(x, 'edges'):
      for x in getattr(x,'edges'):
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
          className = self.__conv__.to_xml_tag(getattr(node,'className'))
        else:
          className = 'obj'
        

        oid = str(getattr(node,'id')) if hasattr(node,'id') else None
        e = ET.Element(className)
        if oid is not None: e.attrib = { 'id': oid }
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

        for i in ['vis', 'receive','send','bgcolor','fgcolor','scale','flag','size','init','nonzero','number','value','hold','intrrpt','digit_width','height', 'log_flag', 'log_height', 'steady', 'subclass', 'name', 'keep']:
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

          # check if we have a struct in the json object
          if hasattr(self.obj,'struct'):
            for idx, s in enumerate(getattr(self.obj,'struct')):
              if getattr(s,'name') == getattr(node,'name'):
                # scalars
                # add the scalar node to the xml element
                self.addScalars(idx, s, e, node)
                
          # text or arrays
          # create the sub element <data>
          data = ET.SubElement(e, 'data')

          if hasattr(node, 'size'):
            ET.SubElement(e, 'size').text = str(getattr(node, 'size'))
          if hasattr(node, 'flag'):
            ET.SubElement(e, 'flag').text = getattr(node, 'flag')

          _data = getattr(node,'data')
          # log(1, 'DATA', _data)

          for d in _data:
            if isinstance(d, str):
              ET.SubElement(data, 'symbol').text = str(d)
            elif isinstance(d, float) or isinstance(d, int):
              ET.SubElement(data, 'float').text = str(d)
            elif isinstance(d, list):
              array = ET.SubElement(data, 'array')
              for f in d:
                ET.SubElement(array, 'float').text = str(f)
            else:
              log(1, 'DATA: unknown format', d)
          
        if hasattr(node,'args'):
          args = getattr(node,'args')
          if not isinstance(args, list):
            args = [args]
          for arg in args:
            ET.SubElement(e, 'arg').text = arg
      
        self.update_with_sub(x, 'border', e)
  
  def getTemplate(self, template):
    if hasattr(self.obj, 'struct'):
      for idx, s in enumerate(getattr(self.obj, 'struct')):
        if getattr(s, 'name') == template:
          return idx, s

  def addScalars(self, idx, s, _parent, _node):
    _data = getattr(_node, 'data')
    if getattr(s,'name') == getattr(_node, 'name'):
      self.addScalar(_parent, idx, s, 'float', _data )
      self.addScalar(_parent, idx, s, 'symbol', _data )
      if hasattr(s,'array'):
        for a in getattr(s,'array'):
          _idx, _s = self.getTemplate(getattr(a,'template'))
          self.addScalars(_idx, _s, _parent, _node)

  def addScalar(self, idx, _struct, _parent, _type, _data):

    if hasattr(_struct,_type):
      # log(1, _type, _struct)
      _struct_floats_ = getattr(_struct,_type)
    
      for d in _data:
        if isinstance(d, str):
          _float_list_ = d.split()
          if len(_float_list_) == len(_struct_floats_):
            for value,name in zip(_float_list_, _struct_floats_):
              ET.SubElement(_parent, name).text = value
        # elif isinstance(d, float) or isinstance(d, int):
          


  def getDeclare(self, x, kind):
    if hasattr(x, kind):
      declares = self.__root__.find('declare')
      if declares is None:
        declares = ET.SubElement(self.__root__, 'declare')
      for x in getattr(x, kind):
        ET.SubElement(declares, kind[:-1]).text = x
      

  def getDependencies(self, x):
    """ Parses the dependencies entry into paths and libs using `getDeclare()` """
    if hasattr(x, "dependencies"):
      self.getDeclare(getattr(x,'dependencies'), 'paths')
      self.getDeclare(getattr(x,'dependencies'), 'libs')

  def getRestore(self, x, cnv):
    # Get the self.depth and remove the last element
    
    self.depth.pop()
    
    if hasattr(x, 'position'):
      position = getattr(x, 'position')
      pos = ET.SubElement(cnv, 'position')
      self.update_with_sub(position, 'x', pos)
      self.update_with_sub(position, 'y', pos)
      self.update_with_sub(x, 'title', cnv)

  def getCoords(self, x, cnv):
    if hasattr(x, 'coords'):
      coords = ET.SubElement(cnv, 'coords')

      a = ET.SubElement(coords, 'a')
      b = ET.SubElement(coords, 'b')

      crds = getattr(x, 'coords')

      if hasattr(crds, 'range'):
        range = getattr(crds, 'range')
        if hasattr(range, 'a'):
          a_range = getattr(range, 'a')
          self.update_with_sub(a_range, 'x', a)
          self.update_with_sub(a_range, 'y', a)
        if hasattr(range, 'b'):
          b_range = getattr(range, 'b')
          self.update_with_sub(b_range, 'x', b)
          self.update_with_sub(b_range, 'y', b)
      
      if hasattr(crds, 'dimension'):
        dimension = ET.SubElement(coords, 'dimension')
        dimen = getattr(crds, 'dimension')
        if hasattr(dimen, 'width'):
          self.update_with_sub(dimen, 'width', dimension)
          self.update_with_sub(dimen, 'height', dimension)
      
      if hasattr(crds, 'gop'):
        self.update_with_sub(crds, 'gop', coords)
      
      if hasattr(crds, 'margin'):
        mgn = ET.SubElement(coords, 'margin')
        margin = getattr(crds, 'margin')
        self.update_with_sub(margin, 'x', mgn)
        self.update_with_sub(margin, 'y', mgn)

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
    
    if hasattr(x, 'id'):
      cnv.set('id', str(x.id))

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
      self.update_with_sub(x, 'vis', cnv)
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


  