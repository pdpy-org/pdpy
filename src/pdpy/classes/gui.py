#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

from .classes import PdObj, Bounds

__all__ = ["PdNativeGui"]

class PdNativeGui(PdObj):
  """ A Pd Native Gui object 
  
  Description
  -----------
  A Pd Native Gui object is a graphical user interface that is implemented in
  pure data. It is a sublcass of the `PdObj`

  Initialization Arguments
  -----------------------
  1. `className`: the name of the class of the object
  2. id: The id of the object
  3. `x`: The x position of the object
  4. `y`: The y position of the object
  5. `digits_width` : The width of the object in digits
  6. lower limit: The lower limit of the object
  7. upper limit: The upper limit of the object
  8. `flag`: The flag of the object
  9. `label`: The label of the object
  10. `receive`: the receiver symbol of the object
  11. `send`: the sender symbol of the object

  """
  def __init__(self, className, *argv):
    super().__init__(*argv[:3])
    self.__pdpy__ = self.__class__.__name__
    self.className = className
    if 3 < len(argv):
      self.digit_width = argv[3]
      self.limits = Bounds(lower=argv[4], upper=argv[5])
      self.flag = argv[6] if 6 < len(argv) else None
      if 7 < len(argv):
        self.label = argv[7] if "-" != argv[7] else None
        self.receive = argv[8] if "-" != argv[8] else None
        self.send = argv[9] if "-" != argv[9] else None

