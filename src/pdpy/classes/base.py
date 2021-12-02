#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Base Class """

from json import dumps as json_dumps
import xml.etree.ElementTree as ET
# from textwrap import wrap
from ..util.utils import log
from .default import Default

__all__ = [ "Base" ]

class Base(object):
  """ Pd Base class
  
  Description
  -----------
  The base class for all pd objects in pdpy.

  Paramaeters
  -----------
  patchname : `str` (optional)
    Name of the Pd patch file (default: `None`)
  pdtype : `str` (optional)
    Type of the Pd object (one of X, N, or A). Defaults to 'X': `#X ...`
  cls : `str` (optional) 
    Class of the Pd object (eg. msg, text, etc.) Defaults to `obj`. `#X obj ...`
  json : `dict` (optional)
    A dictionary of key/value pairs to populate the object. 

  """
  
  def __init__(self, patchname=None, pdtype=None, cls=None, json=None):
    """ Initialize the object """
    self.patchname = patchname
    self.__type__ = pdtype if pdtype is not None else 'X'
    self.__cls__ = cls if cls is not None else 'obj'
    self.__d__ = Default()
    
    if json:
      self.__populate__(self, json)
    
    # The pd line end character sequence
    self.__end__ = ';\r\n' 
    # The pd end symbol for data structures
    self.__semi__ = ' \\;'

  def parent(self, parent=None):
    """ 
    Sets the parent of this object if `parent` is present, 
    otherwise returns the parent of this object.
    """
    if parent is not None:
      self.__parent__ = parent
      # print("adding parent to child", self.__class__.__name__, '<=', parent.__class__.__name__)
      return self
    elif self.__parent__ is not None:
      return self.__parent__
    else:
      raise ValueError("No parent set")

  def __addparents__(self, parent, children='nodes'):
    """ Sets the parents of all children (aka, nodes)
    
    Example:
    __addparents__(self, 'nodes')
    """
    for child in getattr(parent, children, []):
      child.parent(parent)
      # print(child.__pdpy__,repr(dir(child)))
      if hasattr(child, children):
        child.__addparents__(child)

  def __getroot__(self, child):
    """ Returns the parent of this object """
    if hasattr(child, '__parent__'):
      # log(1, child.__class__.__name__, "parented")
      return self.__getroot__(child.__parent__)
    else:
      # log(1, child.__class__.__name__, "has no parent")
      return child

  def __getstruct__(self):
    return getattr(self.__getroot__(self), 'struct', None)

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

  def __json__(self):
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
      indent    = 4
    )
  
  def __dumps__(self):
    log(0, self.__json__())

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
    if n == "True" or n == "true":
      return True
    elif n == "False" or n == "false":
      return False
    else:
      return bool(int(float(n)))

  def __populate__(self, child, json):
    """ Populates the derived/child class instance with a dictionary """
    # TODO: protect against overblowing child scope
    if not hasattr(json, 'items'):
      log(1, child.__class__.__name__, "json is not a dict")
      if not hasattr(json, '__dict__'):
        raise log(2, child.__class__.__name__, "json is not a class")
      json = json.__dict__
    
    # map(lambda k,v: setattr(child, k, v), json.items())
    for k,v in json.items():
      setattr(child, k, v)
    
    if hasattr(child, 'className') and self.__cls__ is None:
      self.__cls__ = child.className 

  def __pd__(self, args=None):
    """ Returns a the pd line for this object
    
    Description
    -----------
    
    Parameters
    -----------
    args : `list` of `str` or `str` or `None`
      The arguments to the pd line.
    
    If args is present, the pd line will end with `;\r\n` with the arguments:
      If args is a list of strings, each element is appended to the pd line.
        `#N canvas 0 22 340 520 12;`
      If args is a string, it is appended to the pd line: 
        `#X obj 10 30 print;`
    If args is None, the pd line is returned without arguments: 
      `#X connect`

    Returns
    -----------
    `str` : the pd line for this object built with `__type__` and `__cls__`

    """
    
    s = f"#{self.__type__} {self.__cls__}"
    # log(1, "Base.__pd__()", repr(s))

    if args is not None:
      if isinstance(args, list):
        s += ' ' + ' '.join(args)
      else:
        s += f' {args}'
        s += self.__end__
    
    s = s.replace('  ', ' ')


    # split line at 80 chars: 
    # insert \r\n on the last space char
    # s = '\n'.join(s[i:i+79] for i in range(0, len(s), 79))
    return s

  def __element__(self, child, text=None, attrib=None):
    """ Returns an XML element for this object """
    if not isinstance(child, str) and hasattr(child, '__pdpy__'):
      child = str(child.__pdpy__).lower()
    element = ET.Element(child)
    if text is not None:
      element.text = str(text)
    if attrib is not None:
      element.attrib = attrib
    return element

  def __subelement__(self, parent, child, **kwargs):
    """ Create a sub element (child) of a parent element (parent) """
    if not isinstance(child, ET.Element):
      child = self.__element__(child, **kwargs)

    return ET.SubElement(parent, child)

