#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
""" XML Converter Class """

from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import parse as __xparse__
from .xmltagconvert import XmlTagConvert
from ..utilities.utils import log

__all__ = [ 'XmlBuilder' ]

class XmlBuilder(XmlTagConvert):
  """ XML Converter Class """
  def __init__(self):
    super().__init__()

  def __tree__(self, root, autoindent=True):
    tree = ElementTree(root)
    if autoindent:
      from xml.etree.ElementTree import indent as __indent__
      __indent__(tree, space='    ', level=0)
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
      __tag__ = super().to_xml_tag(tag)

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
    if super().isvalid(__tag__):
      element = Element(__tag__)
    else:
      element = Element(str(__pdpy__).lower())
   
    if attrib is not None:
      element.attrib.update(attrib)

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

      elem_tag = self.__tag_strip__(elem.tag)
      pdpy_tag = elem.attrib['pdpy'] if 'pdpy' in elem.attrib else None

      
      if elem_tag == 'scalar' and pdpy_tag != 'Array':
        return self.__n__.__get__(name='Scalar')(xml=elem)

      if elem_tag == 'data':
        return {'data':[self.__n__.__get__(name='Data')(xml=c) for c in elem]}

      if elem_tag == 'comments':
        return [self.__n__.__get__(name='Comment')(xml=c) for c in elem]
    
      if elem_tag == 'comment':
        return self.__n__.__get__(name='Comment')(xml=elem)
    
      # print('>'*80)
      # log(1, f"Starting __elem_to_obj__ for {elem_tag}")
      

      # the class
      cls = self.__n__.__get__(name=getattr(elem.attrib, 'pdpy', None), tag=elem_tag)
      # print(cls)
      
      is_list = False
      # Handle list-type tags, we need to create lists for these:
      if elem_tag in ('nodes',   # any node
                      'edges',   # connections
                      'args',    # objects
                      'targets', # messages
                      'messages', # messages
                      # 'data',    # data
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
        print(" ".join(argv))
        log(1, 
          "elem_to_obj\nELEM: "+elem+"\nLENGTH: "+str(len(list(elem)))+"\nTAG: "+str(elem_tag)+ "\nHEAD: "+ str(h)+ "\nHEAD TYPE: "+ str(h_type)+ "\nCLS: "+ str(cls))
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
                  if isinstance(v, list):
                    d.update({subelem_tag:v})
                  # log(1, 'found anything', subelem_tag, v, d)
                  #   for e in v:
                  #     d.update({subelem_tag:e})
                  else:
                    for kk,vv in v.items():
                      d.update({kk:vv})
                else:
                  # log(1, '--------> found header', subelem_tag, v)
                  for _,vv in v.items():
                    d['data'].append(h_type(vv))

      # end subelement loop -----------------------------------------------

      text = elem.text if elem.text is not None else ''
      # tail = elem.tail
      # print('text:',repr(text))
      if '\n' in text:
      # ignore trailing whitespace
        text = text.strip()

      # if text != ' ' and not all([t==' ' for t in text]):
        # text = text.strip()
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
    """ Parse an XML file into an ElementTree object. """
    # PdPyXMLParser(self, xml)
    return __xparse__(xml)
    