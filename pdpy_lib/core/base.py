#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
"""
Base
====
"""

from json import dumps as json_dumps
from ..encoding.xmltagconvert import XmlTagConvert
from ..encoding.xmlbuilder import XmlBuilder
from ..utilities.utils import log
from ..utilities.exceptions import ArgumentException, MalformedName
from ..utilities.default import Default
from ..utilities.namespace import Namespace

__all__ = [ 'Base' ]

class Base(XmlBuilder, XmlTagConvert):
  """ The base class for all pdpy objects

  Parameters
  ----------
  
  patchname : :class:`str` or ``None``
    Name of the Pd patch file (default: ``None``)
  
  pdtype : :class:`str` or ``None``
    Type of the Pd object: ``X``, ``N``, or ``A`` (default: ``X``)
  
  cls : :class:`str`  or ``None``
    Class of the Pd object, eg.: ``msg``, ``text``, ... (default: ``obj``)
  
  json : ``dict`` or ``None``
    A json dictionary of key/value pairs to populate the object.

  xml : ``xml.etree.ElementTree.Element`` or ``None``
    An Xml Element with the appropriate element structure.
  
  default : :class:`pdpy.utilities.default.Default` or ``None``
    A class containing a template for default values.


  .. document private functions
  
  .. automethod:: __pd__
  .. automethod:: __xml_load__
  .. automethod:: __json__
    
  

  """
  
  def __init__(self,
                patchname=None,
                pdtype=None,
                cls=None,
                json=None,
                xml=None,
                default=None):
    """ Initialize the object """
    self.patchname = self.__sane_name__(patchname) # the name of the patch
    self.__type__ = pdtype if pdtype is not None else 'X' # pd's type
    self.__cls__ = cls if cls is not None else 'obj' # pd's class
    self.__d__ = Default() if default is None else default # object defaults
    self.__n__ = Namespace() # pdpy module namespace
    self.__end__ = ';\r\n' # The pd line end character sequence
    self.__semi__ = ' \\;' # The pd end symbol for data structures
    self.__arr_idx__ = 0 # the array index
    XmlTagConvert.__init__(self) # for xml tag conversion (output)
    if json: self.__populate__(self, json) # fill the object with the json data
    if xml:
      XmlBuilder.__init__(self) # initialize the xml base builder class
      tree = XmlBuilder.__xmlparse__(self, xml) # fill the object with xml
      self.__xml_load__(tree)

  def __parent__(self, parent=None, scope=None):
    """ 
    Sets the parent of this object if `parent` is present, 
    otherwise returns the parent of this object.
    """
    if scope is None:
      scope = self
    
    if parent is not None:
      setattr(scope, '__p__', parent)
      # print(f"adding parent {parent.__class__.__name__} to child {self.__class__.__name__}")
      return self
    elif hasattr(self, '__p__'):
      return self.__p__
    else:
      raise ValueError("No parent set in " + self.__class__.__name__)

  def __addparents__(self, parent, children=('nodes','edges','comments')):
    """ Sets the parents of all children """
    # log(1,'addparents: parent <--',parent.__pdpy__)#,repr(dir(child)))
    for c in children:
      for child in getattr(parent, c, []):
        # log(1,f"addparents: child {c} --> ",child.__pdpy__)#,repr(dir(child)))
        # self.__parent__(parent=parent, scope=child)
        setattr(child, '__p__', parent)
        if hasattr(child, c):
          # log(1, 'addparents: child has children')
          self.__addparents__(child)

  def __getroot__(self, child):
    """ Recursively, return the parent root of this object """
    if hasattr(child, '__p__'):
      # log(1, child.__class__.__name__, "parented")
      return self.__getroot__(child.__p__)
    else:
      # log(1, child.__class__.__name__, "has no parent")
      return child

  def __getstruct__(self):
    return getattr(self.__getroot__(self), 'structs', None)

  def __setdata__(self, scope, data, attrib='data'):
    """ Sets the data of the object """
    # log(1, "scope:",scope.__class__.__name__, "data:", data)
    if not hasattr(scope, attrib):
      setattr(scope, attrib, [])
    attribute = getattr(scope, attrib)
    attribute.append(data)
    return attribute[-1]

  def __setattr__(self, name, value):
    """ Hijack setattr to return ourselves as a dictionary """
    if value is not None:
      self.__dict__[name] = value

  def __set_default__(self, kwargs, parameters):
    """ Sets the defaut values or uses the provided keyword argument """
    # print(kwargs, parameters)
    # label = l or iemgui['symbol'],
    #         xoff = default['xoff'],
    #         yoff = default['yoff'],
    #         fface = iemgui['fontface'],
    #         fsize = default['fsize'],
    #         lbcolor = default['lbcolor']
    for param in parameters:
      # print(param)
      k, d = param[:2]
      # print(k)
      # print(d)
      callback = param[2] if len(param) == 3 else lambda x:x
      if k in kwargs:
        v = callback(kwargs.pop(k))
        # print('found', v)
      else:
        # v = d if isinstance(d, dict) else getattr(d, k)
        # print('notfound', k, type(d))
        if isinstance(d, dict):
          # print("d is a dictionary")
          if k in d:
            # print(k,"is in", d)
            v = callback(d[k])
            # print("after callback", v)
          else:
            # print(k,"not in", d)
            v = callback(d)
            # print("after callback", v)
        elif isinstance(d, Default):
          # print("passed Default")
          v = getattr(d, k)
          v = callback(v)
          # print("after callback", v)
        else:
          v = d
        # print('after callback', v)
      # print("setting", k, "with value", v)
      setattr(self, k, v)

  def __json__(self, indent=4):
    """ Return a JSON representation of the instance's scope as a string """

    # inner function to filter out variables that are
    # prefixed with two underscores ('_') 
    # with the exception of '__pdpy__'
    def __filter__(o):
      return { 
        k : v 
        for k,v in o.__dict__.items() 
        if not k.startswith("__") or k=="__pdpy__"
      }

    return json_dumps(
      self,
      default   = __filter__,
      sort_keys = False,
      indent    = indent
    )
  
  def __dumps__(self):
    log(0, self.__class__.__name__, '-'*79,'\n', self.__json__(1))

  def __num__(self, n):
    """ Returns a number (or list of number) object from a Pd file string """
    pdnm = None
    if isinstance(n, str):
      if "#" in n: pdnm = n # skip css-style colors preceded by '#'
      elif ("e" in n or "E" in n) and ("-" in n or "+" in n):
        pdnm = "{:e}".format(int(float(n)))
      elif "." in n: pdnm = float(n)
      else:
        pdnm = int(n)
    elif isinstance(n, list):
      # print("__num__(): input was a list of str numbers", n)
      pdnm = list(map(lambda x:self.__num__(x),n))
    elif 0.0 == n:
      return 0
    else:
      pdnm = n
    return pdnm

  def __pdbool__(self, n):
    """ Returns a boolean object from a Pd file string """
    b = False
    if n == "True" or n == "true":
      b = True
    elif n == "False" or n == "false":
      b = False
    else:
      b = bool(int(float(n)))
    # log(1, "__pdbool__():", n, '->', b)
    return b

  def __isnum__(self, n):
    try:
      n = self.__num__(n)
      return True
    except:
      return False

  def __get_obj_size__(self, parent):
    
    # print(self.__json__())
    font_size = parent.font

    if hasattr(self, 'size') or hasattr(self, 'area'):
      size = self.area if hasattr(self, 'area') else self.size
      # print(self.getname(), "Size", size.__pd__())
      if hasattr(size, 'width') and hasattr(size, 'height'):
        return size.width, size.height
      else:
        if hasattr(size, 'height'):
          if self.className == 'vradio':
            return size.height, size.height * self.number
          else:
            return size.height, size.height
        elif hasattr(size, 'width'):
          return size.width, size.width

    text_h = font_size * 2
    text_w = 0
    
    if hasattr(self, 'className'):
      text_w += len(self.className)
      text_w += 1
    
    if hasattr(self, 'args'):
      text_w += len(' '.join(map(lambda x:str(x),self.args)))
      text_w += 1

    if hasattr(self, 'targets'):
      for target in self.targets:
        if hasattr(target, 'messages'):
          text_w += len(' '.join(target.messages))
          text_w += 1
        text_w += 1
    
    if hasattr(self, 'text'):
      text_w += len(' '.join(self.text))
      text_w += 1

    mod_80 = (text_w-1) // 80

    if mod_80 >= 1: text_h *= mod_80

    return (text_w-1)*font_size//2, text_h


  def __populate__(self, child, json):
    """ Populates the derived/child class instance with a dictionary """
    # TODO: protect against overblowing child scope
    if not hasattr(json, 'items'):
      log(1, child.__class__.__name__, "json is not a dict")
      if not hasattr(json, '__dict__'):
        raise ArgumentException(child.__class__.__name__ + ": json is not a class. It is of type: " + type(json) +"\n"+ json)
      json = json.__dict__
    
    # map(lambda k,v: setattr(child, k, v), json.items())
    for k,v in json.items():
      try:
        v = self.__num__(v)
      except:
        try:
          v = self.__pdbool__(v)
        except:
          pass
      setattr(child, k, v)
    
    if hasattr(child, 'className') and self.__cls__ is None:
      self.__cls__ = child.className 

  def __unescape__(self, argv):
    """ Unescapes the arguments """
    args = []
    for a in argv:
      # unescape the arguments
      if isinstance(a, list):
        a = ' '.join(map(lambda x:str(x).replace('\\','',1), a))
      else:
        a = str(a).replace('\\','',1)

      # and convert them to numbers
      if self.__isnum__(a):
        a = self.__num__(a)
      args.append(a)
    return args

  def __escape__(self, arg):
    """ Escapes the arguments """
    # print("escape:", repr(arg))
    arg = str(arg).replace('\\', '\\\\',1)
    arg = arg.replace(' ', '\\ ',1)
    arg = arg.replace('$', '\\$',1)
    return arg

  def __closeline__(self, pdtype, pdcls, pdargs):
    """ Closes a Pd file line
    """
    s = str("#") + str(pdtype) + " " + str(pdcls)

    if pdargs is not None:
      if isinstance(pdargs, list):
        s += ' ' + ' '.join(pdargs)
      else:
        s += str(" ") + str(pdargs)
        s += self.__end__
    
    s = s.replace('  ', ' ')
    
    return s
  
  def __pd__(self, args=None):
    """ Returns a the pd line for this object
    
    Called by all derived classes to return a Pd line for this object.
    If ``args`` is present the pd line will end with ``;\\r\\n``, and:

    * If ``args`` is a list of strings, each element is appended to the pd line::
    
        #N canvas >>> 0 22 340 520 12 >>> ; <<<
    
    * If ``args`` is a string, it is appended to the pd line::
      
        #X obj >>> 10 30 print >>> ; <<<
    
    * If ``args`` is ``None``, the pd line is returned without arguments::
      
        #X connect >>> <<<

    
    Parameters
    ----------
    args : ``list`` of :class:`str` or :class:`str` or ``None``
      The arguments to the pd line.

    
    Return
    ------
    :class:`str`
      the pd line for this object built with ``__type__`` and ``__cls__``

    """
    
    s = self.__closeline__(self.__type__, self.__cls__, args)
    # log(1, "Base.__pd__()", repr(s))

    # split line at 80 chars: 
    # insert \r\n on the last space char
    # s = '\n'.join(s[i:i+79] for i in range(0, len(s), 79))
    return s

  def __xml_load__(self, xml_tree):
    """ Parse an XML tree into a PdPy object 
    
    Called if loading a PdPy object from an XML file.
    
    .. note:: 
      This method assumes it belongs to a PdPy class, because:
      :class:`pdpy.PdPy` bases :class:`pdpy.Base`
    
    """
    # get the xml root element
    xml_root = xml_tree.getroot()

    # get the encoding
    self.encoding = xml_root.get('encoding', 'utf-8')

    # root element to which we add stuff
    root_dict = {'__p__' : self}

    # find the structs tag
    structs = xml_root.find('structs')
    if structs is not None:
      for n in structs.findall('struct'):
        self.addStruct(xml=n) # belongs to PdPy class
    
    # find the dependencies tag
    for n in xml_root.findall('dependencies'):
      self.addDependencies(xml=n) # belongs to PdPy class

    # go through every element in 'root' and add it to the root_dict
    for n in xml_root.find('root'):
      # print('tag', n.tag)
      if n.tag == 'pdpy' or n.tag == 'root':
        if 'pdpy' in n.attrib:
          root_dict.update({'__pdpy__': n.attrib['pdpy']})
      elif n.tag == 'nodes':
        root_dict.update({
          'nodes': [XmlBuilder.__elem_to_obj__(self, x) for x in n]
        })
      elif n.tag == 'comments':
        root_dict.update({
          'comments': [XmlBuilder.__elem_to_obj__(self, x) for x in n]
        })
      elif n.tag == 'edges':
        root_dict.update({
          'edges': [XmlBuilder.__elem_to_obj__(self, x) for x in n]
        })
      else:
        # an element belonging to canvas' attributes
        o = XmlBuilder.__elem_to_obj__(self, n)
        if hasattr(o, 'items'):
          for k,v in o.items():
            root_dict.update({k:v})
        else:
          root_dict.update({n.tag:o})
    
    # add the root_dict to the PdPy object
    self.addRoot(json=root_dict) # belongs to PdPy class

    # spawn the __parent__ json tree
    self.__jsontree__() # belongs to PdPy class

  def __sane_name__(self, name):
    if name is not None:
      for c in name:
        if c in (";", "$", "&", "|", ",", "`", "%", "*"):
          raise MalformedName("Special chars in name were detected.")
    return name

  def getid(self):
    """ Returns the id attribute or 0 if missing """
    return self.id if hasattr(self, 'id') else 0

  def getname(self):
    """ Returns the className or PdPy class of the object if missing """
    return getattr(self, 'className', self.__class__.__name__)

  def addpos(self, x, y):
    """ Adds or updates the position :class:`pdpy.Point` """
    # print("Adding position for:", self.getname(), x, y)
    if not hasattr(self, 'position'):
      from ..primitives.point import Point
      x = int(x)
      y = int(y)
      setattr(self, 'position', Point(x=x, y=y))
    else:
      self.position.set_x(int(x))
      self.position.set_y(int(y))
