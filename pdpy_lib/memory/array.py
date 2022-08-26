#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
"""
Array
=====
"""

from . import data
from ..objects.obj import Obj

__all__ = [ 'Array' ]

class Array(Obj):
  """ A Pure Data array object
  
  This class represents a Pure Data array or text object.

  Parameters
  ----------
  
  pd_lines : :class:`str`
    The lines of the Pure Data patch that define the object.
  
  json : :class:`dict`
    A JSON representation of the object.
  
  Return
  ------
  
  :class:`pdpy.Array`
    An `Array` object.
  
  """
  def __init__(self, pd_lines=None, json=None, **kwargs):

    self.__pdpy__ = self.__class__.__name__

    if json is not None:
      super().__init__(json=json)

    elif pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      # argc = len(pd_lines) - 4
      # log(1, f"{self.__class__.__name__} argc: {argc}")
      # log(1, 'pd_lines', pd_lines)
      i = 0
      argv = pd_lines[4:]
      # print(argv)
      try:
        # add the border and trim argument list
        if 'f' == argv[len(argv)-2]:
          self.border = argv[-1]
          argv = argv[:-2]

        # print('FIRST',i, argv[i])
        setattr(self, 'subclass', argv[i])
        i += 1
        
        # print('SECOND',i, argv[i])
        if "-k" == argv[i]:
          # print('keeping', i, argv[i])
          setattr(self, 'keep', True)
          i += 1
        
        if '-s' == argv[i]:
          # the struct reference 's'
          # TODO: this should really its own class
          setattr(self, 's', {
            'name' : argv[i + 1], 
            'template' : argv[i + 2]
          })
          i += 3
        
        if '-f' == argv[i]:
          # the struct field reference 'f'
          self.s.update({ 'f' : {
            'name' : argv[i + 1],
            'template' : argv[i + 2]
          }})
          i += 3
        
        # print('THIRD',i, argv[i])
        setattr(self, 'name', argv[i])
        i += 1

        if "-g" == argv[i]:
          setattr(self, 'global', True)
          i += 1
        
        if '-w' == argv[i]:
          wait = self.__num__(argv[i+1]) if argv[i+1].isnumeric() else argv[i+1]
          setattr(self, 'wait', wait)
          i += 2
        
        # print('FOURTH',i, argv[i])
        if 'array' == self.className:
          # TODO: this fix is working
          # but we need a general approach to account for dollarsymbols 
          # as arguments (the value is somewhere else in the patch)
          setattr(self, 'length', self.__num__(argv[i]) if argv[i].isnumeric() else argv[i])
          i += 1
        
        # print('FIFTH',i, argv[i])
        self.addargs(argv[i:])
      
      except IndexError:
        pass
    else:
      super().__init__(cls='obj', className='array')
      
      # canvasbase takes care of incrementing the arrayN counter
      # because it will override the name
      # if it is not set
      if 'name' in kwargs:
        self.name = kwargs.pop('name')

      if 'length' in kwargs:
        self.length = kwargs.pop('length')
      else:
        self.length = self.__d__.array['size']
      
      if 'subclass' in kwargs:
        self.subclass = kwargs.pop('subclass')
      else:
        self.subclass = 'define'      
      
      if 'keep' in kwargs:
        setattr(self, 'keep', True)
      
      if '' in kwargs:
        _data = kwargs.pop('data')
      else:
        _data = [0 for _ in range(1 + self.length)]
      
      if hasattr(self, 'keep'):
        super().__setdata__(self, data.Data(data=_data, head=0))    
  
  def __pd__(self):
    """ Return the pd-lang string for the object. """
    s = ''
    if hasattr(self, 'subclass'):  
      s += str(self.subclass)

    if hasattr(self, 'keep'):
      s += " -k"
    
    if hasattr(self, 's'):
      # the struct reference 's'
      s += " -s " + self.s['name'] + " " + self.s['template']
      if 'f' in self.s:
        # the struct field reference 'f'
        s += " -f " + self.s['f']['name'] + " " + self.s['f']['template']

    if hasattr(self, 'name'):
      s += " " + self.name
    
    if hasattr(self, 'global'):
      s += " -g"
    
    if hasattr(self, 'wait'):
      s += " -w " + " " + str(self.wait)
    
    if hasattr(self, 'length'):
      s += " " + str(self.length)

    return super().__pd__(s)


  def __xml__(self):
    """ Return the XML Element for this object """

    x = super().__xml__(scope=self, tag=self.__cls__, attrib=('subclass', 'name', 'wait', 'length'))

    for e in ('keep', 'global'):
      if hasattr(self, e):
        super().__subelement__(x, e, text = 1 if getattr(self, e) else 0)

    if hasattr(self, 's'):
      # the struct reference 's'
      s = super().__element__(tag='s')
      super().__subelement__(s, 'name', text = self.s['name'])
      super().__subelement__(s, 'template', text = self.s['template'])

      if 'f' in self.s:
        # the struct field reference 'f'
        f = super().__element__(tag='f')
        super().__subelement__(f, 'name', text = self.s['f']['name'])
        super().__subelement__(f, 'template', text = self.s['f']['template'])
        super().__subelement__(s, f)
      
      super().__subelement__(x, s)
    
    return x