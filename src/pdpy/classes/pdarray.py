#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from pdpy.classes.data_structures import PdType
from pdpy.util.utils import log
from .pdobject import PdObject

__all__ = [
  "PdArray"
]

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
  7. If it is an `array`, then the remaining argument is the array `size`

  Returns
  -------
  A `PdArray` object.
  
  """
  def __init__(self, pd_lines = None, json_dict = None):

    self.__pdpy__ = self.__class__.__name__

    if json_dict is not None:
      super().__init__(json_dict=json_dict)

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
          # print('struct-ref', i, argv[i])
          setattr(self, 'struct_ref', {
            'name' : argv[i + 1], 
            'template' : argv[i + 2]
          })
          i += 3
        
        if '-f' == argv[i]:
          # print('element-ref', i, argv[i])
          self.struct_ref.update({ 'element' : {
            'name' : argv[i + 1],
            'template' : argv[i + 2]
          }})
          i += 3
        
        # print('THIRD',i, argv[i])
        setattr(self, 'name', argv[i])
        i += 1
        
        # print('FOURTH',i, argv[i])
        setattr(self, 'size', self.num(argv[i]))
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
      if hasattr(self, 'name'):
        s += f" {self.name}"
      if "array" == self.className and hasattr(self, 'size'):
        s += f" {self.size}"
      if hasattr(self, 'struct_ref'):
        s += f" -s {self.struct_ref['name']} {self.struct_ref['template']}"
        if 'element' in self.struct_ref:
          s += f" -f {self.struct_ref['element']['name']} {self.struct_ref['element']['template']}"
    return super().__pd__(s)
