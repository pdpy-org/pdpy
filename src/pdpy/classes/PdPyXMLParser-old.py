#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" PdPyXMLParser Class Definition """

from io import IOBase
import json
import xml.etree.ElementTree as ET
from pdpy.util.utils import log
from .default import Namespace
from collections import defaultdict

__all__ = [
  "PdPyXMLParser"
]

class PdPyXMLParser:

  def __init__(self, parent, xml):
    self.elements = []
    # self.attributes = []
    # self.classes = []
    # self.last = ()
    # keep track of the depth of the xml structure
    # self.__canvas_idx__ = []
    # self.__depth__ = 0
    # the flat list holding all tags
    # self.__tag__ = []
    # the flat list of dicts holding all objects
    # self.__obj__ = defaultdict(list)
    # the list of lists holding the objects
    # self.__objects__ = []
    # the pdpy parent object
    # self.__parent__ = parent
    # the pdpy module namespace
    self.__n__ = Namespace()
    # the parser object to which we pass this class as target
    parser = ET.XMLParser(target=self)
    
    # check if the xml is a file or a string
    if isinstance(xml, IOBase):
      # if it is a file, parse it, the `target` takes care of the rest
      ET.parse(xml, parser=parser)
    else:
      print("__init__(): xml is a string:", xml)


  # def addRoot(self, argv):
  #   self.root = Canvas(json={
  #           'name' : self.patchname,
  #           'vis' : 1,
  #           'id' : None, 
  #           'screen' : Point(x=argv[0], y=argv[1]),
  #           'dimension' : Size(w=argv[2], h=argv[3]), 
  #           'font' : int(argv[4]),
  #           'isroot' : True,
  #           '__parent__' : self
  #   })
  #   return self.root

  # def __last_canvas__(self):
  #   """ Returns the most recent canvas (from the nodes list)

  #   Description
  #   -----------
  #   1. Start at the root canvas
  #   2. Do `__depth__` amount of iterations (0 depth will return `self.root`)
  #   3. Get the `canvas_node_index` by indexing `__canvas_idx__` with `__depth__`
  #   4. Return the canvas located at that `canvas_node_index`
  #   """
    
  #   __canvas__ = self.root
  #   for idx in range(self.__depth__):
  #     canvas_node_index = self.__canvas_idx__[idx]
  #     __canvas__ = __canvas__.nodes[canvas_node_index]
  
  #   return __canvas__

  def __check__(self, tag, attrib):
    __pdpy__ = self.__n__.get(name=getattr(attrib, 'pdpy', None), tag=tag)
    if __pdpy__ is None:
      raise KeyError(f"No PdPy class found for element: {tag}")
    return __pdpy__

  def __get_canvas__(self):
    """ Return the last canvas taking depth and incrementing object index count
    """
    # __canvas__ = self.root if self.__depth__ == 0 else self.__last_canvas__()
    __canvas__ = self.__last_canvas__()
    self.__obj_idx__ = __canvas__.grow()
    self.__depth__ += 1
    return __canvas__

  # def addCanvas(self, argv):
  #   """ Add a Canvas object from pure data syntax tokens
    
  #   Description:
  #   ------------
  #   This 
  #   """
  #   __canvas__ = self.__get_canvas__()
  #   canvas = Canvas(json={
  #           'name'   : argv[4],
  #           'vis'    : self.__num__(argv[5]),
  #           'id'     : self.__obj_idx__,
  #           'screen' : Point(x=argv[0], y=argv[1]), 
  #           'dimension' : Size(w=argv[2], h=argv[3]),
  #   })
  #   self.__canvas_idx__.append(__canvas__.add(canvas))

  #   return canvas

  # def restore(self, argv=None):
  #   """ Restore constructor
  #   """
  #   # restored canvases also have borders
  #   # log(0,"RESTORE",argv)
  #   last = self.__last_canvas__()
  #   if argv is not None:
  #     setattr(last, 'position', Point(x=argv[0], y=argv[1]))
  #     setattr(self.__last_canvas__(), 'title', ' '.join(argv[2:]))
  #   self.__depth__ -= 1
  #   if len(self.__canvas_idx__):
  #     self.__canvas_idx__.pop()
  #   return last

  def start(self, tag, attrib):
    # print('start:',tag, attrib)
    isobj = isinstance(self.__check__(tag, attrib), type)
    self.elements.append({
      tag:attrib,
      'isobj':isobj
    })
    if isobj:
      self.elements[-1]['json'] = list()
    # increment depth
    # self.__depth__ += 1
    
    # store the tag
    # self.__last_tag__ = tag
    # cls = self.__check__(tag, attrib)
    # isobj= isinstance(cls, type)

    # obj = defaultdict(list,{
    #   'tag':tag,
    #   'attrib':attrib,
    #   'isobj':isobj,
    #   'class':str(cls)
    # })
    
    # if isobj:
      # self.classes.append(obj)
    # else:
      # self.attributes.append(obj)
    # if attrib is not None and attrib != {}:
      # obj['@attrib'].append(attrib)
    
    # add the obj to the stack
    # self.__obj__[tag].append({tag:attrib})
    
    # get the index to the last obj
    # self.last = [isobj,len(self.classes)-1,len(self.attributes)-1]

    # self.__last_idx__ = len(self.__obj__) - 1
    
  def data(self, data):
    # print('data:',data)
    data = data.strip() # remove whitespace
    # only add data if it is not empty 
    if data is not None and data != '':
      self.elements[-1].update({'data':data})
      # create a new dict for the data
      # update the last object with the data dict
      # self.__obj__[self.__last_idx__].append(data)
      # if self.last[0]:
      #   # last object was a type
      #   tag = self.classes[-1]['tag']
      #   # attrib = self.classes[-1]['attrib']
      #   obj = {
      #     tag : data
      #   }
      #   self.classes[-1]['json'].append(obj)
      # else:
      #   tag = self.attributes[-1]['tag']
      #   # attrib = self.classes[-1]['attrib']
      #   obj = {
      #     tag : data
      #   }
      #   self.attributes[-1].update(obj)
      #   # last object was an attribute

      
  def end(self, tag):
    # print('end:',tag)
    if len(self.elements) > 1:
      obj = self.elements.pop()
      
      for i in range(len(self.elements), 0, -1):
        if i < len(self.elements) and 'json' in self.elements[i]:
          self.elements[i]['json'].append(obj)
          break

    # if len(self.classes) <= 1 or len(self.attributes) <= 1: return
    
    # if self.last[0]:
    #   o = self.classes.pop()
    #   self.classes[-1][o['tag']].append(o)
    # else:
    #   a = self.attributes.pop()
    #   self.classes[-1]['json'].append(a)
    
    # self.last = [self.classes[-1]['isobj'], len(self.classes)-1, len(self.attributes)-1]

    # decrement depth
    # self.__depth__ -= 1
    
    # remove the obj from the stack
    # and add it to the objects list


    # def jsonify(obj):
    #   for k,v in obj.items():
    #     if isinstance(v, list):
    #       for e in v:
    #         if isinstance(e, defaultdict):
    #           c = jsonify(e, indent=indent*2, c=c)
    #         else:
    #           c = p(indent, 'B', k, e, c=c)
    #     else:
    #       c = p(indent,'A',k,v, c=c)
    #   return c







    # if len(self.__obj__) > 1:
      # print(type(self.__obj__[self.__last_idx__][tag]))
      # isobj = isinstance(self.__obj__[self.__last_tag__], type)
      # obj = self.__obj__.pop(tag)
      # if isobj:
        # pass
        # json_dict = {}
        
        # def _jsonify(obj, json_dict=json_dict):
        #   for o in obj:
        #     if isinstance(o, dict):
        #       for k,v in o.items():
        #         k = k.replace('@', '')
        #         if isinstance(v, list):
        #           for e in v:
        #             if isinstance(e, defaultdict):
        #               e = _jsonify(e, json_dict={})
        #             json_dict.update({k:e})
        #         else:
        #           json_dict.update({k:v})
        #     else:
        #       print(f"{o} is not a defaultdict")
        #       # json_dict.update({o:None})
        #       continue

        #   return json_dict
        
        # json_dict = _jsonify(obj[f"@json"], json_dict=json_dict)
        
        # # json_dict = {}.fromkeys(*list(map(lambda d:dict(d), obj[f"@json"])))
        # print(json_dict)
        # # self.__obj__[self.__last_idx__-1]['@json'].append(obj)
        # a = tuple(**obj[f"@attrib"]) if obj[f"@attrib"] else ()
        # o = obj[tag](*a, json=json_dict)
        # o.__dumps__()
      # else:
        # self.__obj__[self.__last_idx__-1]['@json'].append(obj)
      # print(isobj)
        # print(o)
        # self.__obj__[self.__last_idx__-1] = o
      # self.__objects__.append()
      # self.__last_idx__ = len(self.__obj__) - 1
        

  def close(self):
    # print('close')
    print("*"*80)
    print(json.dumps(self.elements, indent=2))
    # c = 0
    
    # def p(*e, c=c):
    #   print(c, *e)
    #   c += 1
    #   return c
    





    # def _print(obj, indent='-', c=c):
    #   for k,v in obj.items():
    #     if isinstance(v, list):
    #       for e in v:
    #         if isinstance(e, defaultdict):
    #           c = _print(e, indent=indent*2, c=c)
    #         else:
    #           c = p(indent, 'B', k, e, c=c)
    #     else:
    #       c = p(indent,'A',k,v, c=c)
    #   return c
    
    # _print(self.classes[0], c=c)

    # def _print2(obj):
    #   for k,v in obj.items():

    #     if isinstance(v, list):
    #       for e in v:
    #         if isinstance(e, defaultdict):
    #           _print2(e)
    #         else:
    #           print(k, e)
    #     else:
    #       print(k, v)
          
    # # _print2(self.__obj__[0])

    # def _inst(obj):
    #   o=[]
    #   for k, v in obj.items():
    #     if isinstance(v, list):
    #       for e in v:
    #         if isinstance(e, defaultdict):
    #           o.append(_inst(e))
    #         else:
    #           o.append({k : str(e)})
    #     else:
    #       o.append({k : str(v)})
    #   return o

    # # for i,v in self.__obj__[0].items():
    #   # o = json.loads(v, object_hook=lambda d: str(d))
    #   # print(i, v)
    #   # print(json.dumps(o, indent=2))
    # # d = _inst(self.__obj__[0])
    # # print(json.dumps(d, indent=2))

  
