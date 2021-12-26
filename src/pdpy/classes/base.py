#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Base Class """

from json import dumps as json_dumps
from xml.etree.ElementTree import ElementTree, Element, indent, parse as xparse

from pdpy.classes.exceptions import ArgumentException
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
    elif self.__p__ is not None:
      return self.__p__
    else:
      raise ValueError("No parent set")

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

  def __populate__(self, child, json):
    """ Populates the derived/child class instance with a dictionary """
    # TODO: protect against overblowing child scope
    if not hasattr(json, 'items'):
      log(1, child.__class__.__name__, "json is not a dict")
      if not hasattr(json, '__dict__'):
        raise ArgumentException(f"{child.__class__.__name__}: json is not a class. It is of type: {type(json)}:\n{json}")
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
    
    # protect against empty string on the tag for 'empty' objects
    if tag == '': tag = None

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

    # log(1, f"""element
    #   tag: {__tag__}
    #   text: {text}
    #   attrib: {attrib}
    #   """)

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
    # print(parent, scope, attrib)
    
    def _parseattrib(a):
      for e in a:
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
    
    if attrib is not None:
      # log(0, 'Updating attrib:', attrib)
      if type(attrib) in (list, tuple):
        _parseattrib(attrib)
      elif isinstance(attrib, str):
        _parseattrib([attrib])
      else:
        # print("----- DICT ATTIRB: ",attrib)
        # for k,v in attrib.items():
          # parent.attrib.update({k:v})
        pass
    else:
      # log(1, "MISSING ATTRIBUTES:",parent, scope, attrib)
      pass

  def __update_attrib__(self, element, key, value):
    element.attrib.update({key: str(value)})

  def __xml__(self, scope=None, tag=None, attrib=None):
    # print("base",scope, tag, attrib)
    x = self.__element__(scope=scope, tag=tag)
    self.__update_element__(x, scope, attrib)
    return x
  

  def __tag_strip__(self, tag):
      strip_ns_tag = tag
      split_array = tag.split('}')
      if len(split_array) > 1:
          strip_ns_tag = split_array[1]
          tag = strip_ns_tag
      return tag


  def __elem_to_obj__(self, elem):
      """Convert an Element into an object """

      elem_tag = elem.tag
      
      if elem_tag == 'scalar':
        return self.__n__.__get__(name='Scalar')(xml=elem)

      # print('>'*80)
      # log(1, f"Starting __elem_to_obj__ for {elem_tag}")
      elem_tag = self.__tag_strip__(elem.tag)
      

      # the class
      cls = self.__n__.__get__(name=getattr(elem.attrib, 'pdpy', None), tag=elem_tag)
      # print(cls)
      
      is_list = False
      # Handle list-type tags, we need to create lists for these:
      if elem_tag in ('nodes',   # any node
                      'edges',   # connections
                      'args',    # objects
                      'comments',# comments
                      'targets', # messages
                      'message', # messages
                      # 'floats',  # scalars
                      # 'symbols', # scalars
                      # 'texts',   # scalars
                      # 'arrays',   # scalars
                      ):
        is_list = True
        d = [] # a list of PdData objects
      else:
        d = {} # our usual dictionary

      # handle header and data type loading
      h = elem.attrib['header'] if 'header' in elem.attrib else None
      h_type = str if h and h in ('set','saved') else self.__num__
      
      # d will be a PdData type if header was found
      if h is not None:
        d.update({'__pdpy__':'PdData'})
        d.update({'data':[]})
        d.update({'header':h})
      
      def _prnt(*argv):   
        print(*argv)
        log(1, 
          f"""elem_to_obj
          ELEM: {elem}
          LENGTH: {len(list(elem))}
          TAG: {elem_tag}
          HEAD: {h}
          HEAD TYPE: {h_type}
          CLS: {cls}
          """)
      # _prnt('')
      # loop over subelements to merge them ----------------------------------
      for subelem in elem:
        
        subelem_tag = self.__tag_strip__(subelem.tag)

        # recurse into 'v'
        # print('->'*40)
        # log(1, f"-- BEGIN recursion __elem_to_obj__ for {elem_tag}")
        # log(1, f"""subelement loop
        # SUBELEMENT: {subelem}
        # TAG: {subelem_tag}
        # """)
        v = self.__elem_to_obj__(subelem)
        # log(1, f"-- END recursion __elem_to_obj__ for {elem_tag}")
        # print('<-'*40)
        if 'pdpy' in subelem.attrib:
          # sub_cls = self.__n__.__get__(name=getattr(subelem.attrib, 'pdpy', None), subelem_tag=subelem_tag)
          # print("Found subclass",sub_cls)
          if is_list:
            d.append(v)
          else:
            d.update({subelem_tag: v})
        else:
          # print(d, subelem_tag, v)
          if not isinstance(d, dict) and is_list:
            # _prnt("Found list", subelem_tag, '-->', v)
            # drop the keys of the <msg> tag and keep values only
            if isinstance(v, dict):
              d += v.values()
            else:
              # these are proper xml Element objects, not dicts
              d.append(v)
          else:
            if type(v) not in (dict, list, str, int, float, bool):
              # log(1, 'not a dict', subelem_tag, v)
              d.update({subelem_tag: v})
            else:
              if 'text' in v:
                # a pd comment is a string
                # log(1, 'found comment', subelem_tag, v)
                d.update({'text':[t for t in [v['text']]]})
              else:
                if h is None:
                  # if isinstance(v, list):
                    # d.update({subelem_tag:v})
                  # log(1, 'found anything', subelem_tag, v)
                  #   for e in v:
                  #     d.update({subelem_tag:e})
                  # else:
                  for kk,vv in v.items():
                    d.update({kk:vv})
                else:
                  # log(1, '--------> found header', subelem_tag, v)
                  for _,vv in v.items():
                    d['data'].append(h_type(vv))

      # end subelement loop -----------------------------------------------

      text = elem.text
      # tail = elem.tail
      
      # ignore leading and trailing whitespace
      if text:
        text = text.strip()
      # if tail:
        # tail = tail.strip()

      # if tail:
        # d['#tail'] = tail
        # print("FOUND TAIL", tail)

      if d:
        # use #text element if other attributes exist
        if text:
            d["#text"] = text
      else:
        # text is the value if no attributes
        d = text or None
      
      if isinstance(cls, str) and not 'pdpy' in elem.attrib:
        if 'arg' == elem_tag:
          return d
        else:
          return {elem_tag: d}
      elif d is None:
        cls = self.__n__.__get__(name=elem_tag)
        if not isinstance(cls, str):
          # print("FOUND CLASS", cls)
          # log(1, f"Ending __elem_to_obj__ for {elem_tag}")
          # print('<'*80)
          return cls()
        else:
          _prnt("DICT IS", d)
      else:
        try:
          # log(1,'UPDATING:',d)
          if 'pdpy' in elem.attrib and isinstance(d, dict):
            cls = self.__n__.__get__(name=elem.attrib['pdpy'])
            c = cls(json=d)
          elif isinstance(d, list):
            c = d
          else:
            # _prnt(f"updating: {d}")
            cls = self.__n__.__get__(name=d.get('__pdpy__',None), tag=elem_tag)
            if isinstance(cls, type):
              c = cls(json=d)
            else:
              log(2,"Unknown JSON object:", d)
          # print('-'*80)
          # c.__dumps__()
        except Exception as e:
          log(2, e)
          log(2, cls, d)
          c = None
        finally:
          # log(1, f"Ending __elem_to_obj__ for {elem_tag}")
          # print('<'*80)
          return c

  def __xmlparse__(self, xml):
    """ Parse an XML element into a PdPy object """
    # PdPyXMLParser(self, xml)
    xml_tree = xparse(xml)
    xml_root = xml_tree.getroot()
    self.encoding = xml_root.get('encoding', 'utf-8')
    
    # root element to which we add stuff
    root_dict = {'__p__' : self}

    # find the structs tag
    structs = xml_root.find('structs')
    if structs is not None:
      for n in structs.findall('struct'):
        self.addStruct(xml=n)
    
    # find the dependencies tag
    for n in xml_root.findall('dependencies'):
      self.addDependencies(xml=n)

    # go through every element in 'root' and add it to the root_dict
    for n in xml_root.find('root'):
      # print('tag', n.tag)
      if n.tag == 'pdpy' or n.tag == 'root':
        if 'pdpy' in n.attrib:
          root_dict.update({'__pdpy__': n.attrib['pdpy']})
      elif n.tag == 'nodes': 
        root_dict.update({'nodes': [self.__elem_to_obj__(x) for x in n]})
      elif n.tag == 'comments':
        root_dict.update({'comments': [self.__elem_to_obj__(x) for x in n]})
      elif n.tag == 'edges':
        root_dict.update({'edges': [self.__elem_to_obj__(x) for x in n]})
      else:
        # an element belonging to canvas' attributes
        o = self.__elem_to_obj__(n)
        if hasattr(o, 'items'):
          for k,v in o.items():
            root_dict.update({k:v})
        else:
          root_dict.update({n.tag:o})
    
    # these method is an attribute of the PdPy class
    # add the root_dict to the PdPy object
    self.addRoot(json=root_dict)
    # spawn the __parent__ json tree
    self.__jsontree__()

  def __jsontree__(self):
    # log(0, f"{self.__class__.__name__}.__jsontree__()")
    setattr(self.root, '__p__', self)
    for x in getattr(self, 'structs', []):
      setattr(x, '__p__', self)
    self.__addparents__(self.root)
