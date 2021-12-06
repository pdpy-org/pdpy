#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Base Class """

from json import dumps as json_dumps
from .PdPyXMLParser import PdPyXMLParser
from xml.etree.ElementTree import ElementTree, Element, indent #, tostring
# from textwrap import wrap
from ..util.utils import log
from .default import Default, XmlTagConvert, Namespace

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
  
  def __init__(self,
                patchname=None,
                pdtype=None,
                cls=None,
                json=None,
                xml=None,
                default=None):
    """ Initialize the object """
    self.patchname = patchname # the name of the patch
    self.__type__ = pdtype if pdtype is not None else 'X' # pd's type
    self.__cls__ = cls if cls is not None else 'obj' # pd's class
    self.__d__ = Default() if default is None else default # object defaults
    self.__c__ = XmlTagConvert() # utility for converting xml tags
    self.__n__ = Namespace() # pdpy module namespace
    self.__end__ = ';\r\n' # The pd line end character sequence
    self.__semi__ = ' \\;' # The pd end symbol for data structures
    if json: self.__populate__(self, json) # fill the object with the json data
    if xml: self.__xmlparse__(xml) # fill the object with the xml data

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

  def __tree__(self, root, autoindent=True):
    tree = ElementTree(root)
    if autoindent:
      indent(tree, space='    ', level=0)
    # return tostring(self.__root__, encoding='unicode', method='xml')
    return tree

  def __element__(self, scope=None, tag=None, text=None, attrib=None):
    """ Returns an XML element for this object """
    __pdpy__ = None
    __tag__ = None
    
    if tag is not None and isinstance(tag, str):
      # we have a tag, so the element will have a 
      # different name than the PdPy class name
      # we will need to put the PdPy class name
      # in the '__pdpy__' attribute

      # convert the tag to xml-friendly format
      __tag__ = self.__c__.to_xml_tag(tag)

    if scope is not None and hasattr(scope, '__pdpy__'):
      # we have a scope, so we know the PdPy class name
      # we can create the element with the PdPy class name
      # and omit the '__pdpy__' attribute
      
      # get the pdpy name for the scope
      __pdpy__ = getattr(scope, '__pdpy__')

    if __tag__ is not None and __pdpy__ is not None:
      # we have both a tag and a scope
      
      # store the class name in the attributes
      # update the attrib dict if it's there
      if attrib is not None:
        attrib.update({'pdpy':__pdpy__})
      else:
        attrib = {'pdpy':__pdpy__}
    
    elif __tag__ is not None and __pdpy__ is None:
      # we have a tag, but no scope
      # we don't update the attrib dict
      pass

    elif __pdpy__ is not None and __tag__ is None:
      # we have a scope, but no tag
      # we don't update the attrib dict
      # but we need to set the tag to the PdPy class name
      __tag__ = str(__pdpy__).lower()

    else:
      # we have neither a tag nor a scope
      raise AttributeError("Either tag or scope must be present")

    # create the element
    if attrib is not None:
      element = Element(__tag__, attrib=attrib)
    else:
      element = Element(__tag__)

    # store the text of the element as a string
    if text is not None:
      element.text = str(text)
    
    return element

  def __subelement__(self, parent, child, **kwargs):
    """ Create a sub element (child) of a parent element (parent) """
    if not isinstance(child, Element):
      if isinstance(child, str):
        child = self.__element__(tag=child, **kwargs)
      else:
        child = self.__element__(scope=child, **kwargs)
    parent.append(child)

  def __update_element__(self, parent, scope, attrib):
    """ Updates an element's attributes 
    
    Description
    -----------
    This method is used to update an element with pdpy attributes.
    The element is updated with the attributes of the scope.

    Parameters
    -----------
    parent : `Element`
      The element to update
    scope : `object`
      The PdPy object handle (aka, `self`) to update the element with
    attrib : `list` or `tuple` of `str` 
      The list of attributes to update the element with

    """
    if attrib is not None:
      for e in attrib:
        if hasattr(scope, e):
          attr = getattr(scope, e)
          if hasattr(attr, '__xml__'):
            self.__subelement__(parent, getattr(scope,e).__xml__(e))
          else:
            if type(attr) in (list, tuple):
              for a in attr:
                if hasattr(a, '__xml__'):
                  self.__subelement__(parent, a.__xml__(e))
                else:
                  self.__subelement__(parent, e, text=a)
            else:
              self.__subelement__(parent, e, text=attr)

  def __xml__(self, scope=None, tag=None, attrib=None):
    x = self.__element__(scope=scope, tag=tag)
    self.__update_element__(x, scope, attrib)

    return x
  
  def __xmlparse__(self, xml):
    """ Parse an XML element into a PdPy object """
    PdPyXMLParser(self, xml)
    