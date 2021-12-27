#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" PdArray Class Definition """

from .pdobject import PdObject

__all__ = [ 'PdArray' ]

class PdArray(PdObject):
  """ A Pure Data array object
  
  Description
  -----------
  This class represents a Pure Data array or text object.

  Initialization Arguments
  ----------
  The first four arguments correspond to the `PdObject` arguments. 
  See the `PdObject` class.
  1. `id`: The id of the pd object.
  2. `x`: The x-coordinate of the pd object.
  3. `y`: The y-coordinate of the pd object.
  4. `className`: The class name of the array.
  5. `subclass`: The sub family of the array, eg. `define` or `sum`, etc.
  6. `-k` flag (optional), or `name`: the name of the array
  7. If it is an `array`, then the remaining argument is the array `length`

  Returns
  -------
  A `PdArray` object.
  
  """
  def __init__(self, pd_lines = None, json = None):

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


  def __pd__(self):
    """ Return the pd code of the object. """
    s = ''
    if hasattr(self, 'subclass'):  
      s += f"{self.subclass}"

    if hasattr(self, 'keep'):
      s += " -k"
    
    if hasattr(self, 's'):
      # the struct reference 's'
      s += f" -s {self.s['name']} {self.s['template']}"
      if 'f' in self.s:
        # the struct field reference 'f'
        s += f" -f {self.s['f']['name']} {self.s['f']['template']}"

    if hasattr(self, 'name'):
      s += f" {self.name}"
    
    if hasattr(self, 'global'):
      s += " -g"
    
    if hasattr(self, 'wait'):
      s += f" -w {self.wait}"
    
    if hasattr(self, 'length'):
      s += f" {self.length}"

    return super().__pd__(s)


  def __xml__(self):
    """ Return the XML Element for this object """

    x = super().__xml__(scope=self, attrib=('subclass', 'name', 'wait', 'length'))

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