#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" IEMGUI Class Definitions """

from .base import Base
from .classes import Point, Size, Bounds
from .connections import Comm
from .pdobject import PdObject
from .default import PdFonts

__all__ = [ 
  "IEMLabel",
  "PdFont",
  "Vu",
  "Toggle",
  "Cnv",
  "Radio",
  "Bng",
  "Nbx",
  "Slider"
]

class PdFont(Base):
  def __init__(self, face=None, size=None, json=None):
    if face is not None and size is not None:
      self.__pdpy__ = self.__class__.__name__
      self.face = self.__num__(face)
      self.name = PdFonts[self.face if self.face < len(PdFonts) else -1]
      self.size = self.__num__(size)
    elif json is not None:
      super().__populate__(self, json)
  
  def __pd__(self):
    """ Return the pd lines for this object """
    return f"{self.face} {self.size}"

# end class PdFont -----------------------------------------------------------

class IEMLabel(Base):
  """ 
  The IEM Label Object
  ====================

  Description
  -----------
  This is the base class for the IEM gui.

  Initialization Arguments
  ------------------------
  1. `label`: the label text
  2. `x`: the x-offset of the label
  3. `y`: the y-offset of the label
  4. `fface`: the font face of the label
  5. `fsize`: the font size of the label
  6. `lbcolor`: the color of the label
  """
  def __init__(self,
              label=None,
              xoff=None,
              yoff=None,
              fface=None,
              fsize=None,
              lbcolor=None,
              json=None):
    if json is not None:
      super().__populate__(self, json)

    else:
      self.__pdpy__ = self.__class__.__name__
      self.label = label if label is not None else self.__d__.iemgui['symbol']
      self.offset = Point(xoff, yoff)
      self.font = PdFont(fface, fsize)
      self.lbcolor = self.__num__(lbcolor)

  def __pd__(self):
    """ Return the pd string for this iem label """
    return f"{self.label} {self.offset.__pd__()} {self.font.__pd__()}"

# end of class IEMLabel --------------------------------------------------------

class Vu(PdObject):
  """ 
  The IEM Vu Object
  ==================

  The IEM gui object is a vu meter.

  1. 5: `width`: the width of the vu meter area
  2. 6: `height`: the height of the vu meter area
  3. 7: `receive`: the receiver symbol of the vu meter
  4. 8-13: `IEMLabel` Parameters
  5. 14: `scale`: flag to draw the dB scale or not
  6. 15: `flag`: another flag.
  """

  def __init__(self, pd_lines=None, json=None):
    self.__pdpy__ = self.__class__.__name__
    if pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      pd_lines = pd_lines[4:]
      self.area = Size(*pd_lines[:2])
      self.comm = Comm(send=False, receive=pd_lines[2])
      self.label = IEMLabel(*pd_lines[3:8], pd_lines[9])
      self.bgcolor = self.__num__(pd_lines[8])
      self.scale= self.__pdbool__(pd_lines[10]) if 10 < len(pd_lines) else None
      self.flag = self.__pdbool__(pd_lines[11]) if 11 < len(pd_lines) else None
    elif json is not None:
      super().__init__(json=json)

  def __pd__(self):
    """ Return the pd string for this object """
    s = self.area.__pd__()
    s += f" {self.comm.__pd__()}"
    s += f" {self.label.__pd__()}"
    s += f" {self.bgcolor}"
    s += f" {self.label.lbcolor}"
    if hasattr(self, 'scale') and self.scale is not None:
      s += f" {1 if self.scale else 0}"
    if hasattr(self, 'flag') and self.flag is not None:
      s += f" {1 if self.flag else 0}"
    return super().__pd__(s)
class Toggle(PdObject):
  """
  The IEM Toggle Object
  ======================

  The case of `tgl`
  --------------------
  
  The IEM gui object is a Toggle button.

  1. 5: `size`: the size of the toggle square
  2. 6: `init`: the init flag to trigger the toggle on loadtime
  3. 7: `send`: the sender symbol of the toggle
  3. 8: `receive`: the receiver symbol of the toggle
  4. 9-14: `IEMLabel` Parameters
  5. 15: `flag`: a flag
  6. 16: `nonzero`: the non-zero value when toggle is on.
  """

  def __init__(self, pd_lines=None, json=None):
    self.__pdpy__ = self.__class__.__name__
    if pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      pd_lines = pd_lines[4:]
      self.size = self.__num__(pd_lines[0])
      self.init = self.__pdbool__(pd_lines[1])
      self.comm = Comm(send=pd_lines[2], receive=pd_lines[3])
      self.label = IEMLabel(*pd_lines[4:9], pd_lines[11])
      self.bgcolor = self.__num__(pd_lines[9])
      self.fgcolor = self.__num__(pd_lines[10])
      self.flag    = self.__num__(pd_lines[12])
      self.nonzero = self.__num__(pd_lines[13])
    elif json is not None:
      super().__init__(json=json)

  def __pd__(self):
    """ Return the pd string for this object """
    s = str(self.size)
    s += f" {1 if self.init else 0}"
    s += f" {self.comm.__pd__()}"
    s += f" {self.label.__pd__()}"
    s += f" {self.bgcolor}"
    s += f" {self.label.lbcolor}"
    s += f" {self.fgcolor}"
    s += f" {1 if self.flag else 0}"
    s += f" {self.nonzero}"
    return super().__pd__(s)

class Cnv(PdObject):
  """
  The IEM Canvas Object
  ======================
      The case of `cnv` or `my_canvas`
    --------------------
    
    The IEM gui object is a IEM canvas.

    1. 5: `size`: the size of the canvas mouse selection box
    2. 6: `width`: the width of the canvas area
    2. 7: `height`: the height of the canvas area
    3. 8: `send`: the sender symbol of the canvas # why is this here?
    3. 9: `receive`: the receiver symbol of the toggle
    4. 10-15: `IEMLabel` Parameters
    5. 16: `flag`: a flag
  """
  def __init__(self, pd_lines=None, json=None):
    self.__pdpy__ = self.__class__.__name__
    if pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      pd_lines = pd_lines[4:]
      self.size = self.__num__(pd_lines[0])
      self.area = Size(*pd_lines[1:3])
      if 12 < len(pd_lines):
        self.comm = Comm(send=pd_lines[3], receive=pd_lines[4])
        off = 0
      else:
        self.comm = Comm(send=False,receive=pd_lines[3])
        off = 1
      self.label = IEMLabel(*pd_lines[5-off:10-off], pd_lines[11-off])
      self.bgcolor = self.__num__(pd_lines[10-off])
      self.flag    = self.__num__(pd_lines[12-off])
    elif json is not None:
      super().__init__(json=json)
  
  def __pd__(self):
    """ Return the pd string for this object """
    s = str(self.size)
    s += f" {self.area.__pd__()}"
    s += f" {self.comm.__pd__()}"
    s += f" {self.label.__pd__()}"
    s += f" {self.bgcolor}"
    s += f" {self.label.lbcolor}"
    s += f" {1 if self.flag else 0}"
    return super().__pd__(s)
class Radio(PdObject):
  """
  The IEM Radio Object
  =====================
  The case of `hradio` or `vradio`
  --------------------
  
  The IEM gui object is a IEM horizontal or vertica radio button.

  1. 5: `size`: the size of each radio button
  2. 6: `flag`: a flag
  2. 7: `init`: the init flag to trigger the radio on loadtime
  2. 8: `number`: the number of buttons
  3. 9: `send`: the sender symbol of the radio
  3. 10: `receive`: the receiver symbol of the radio
  4. 11-16: `IEMLabel` Parameters
  5. 17: `value`: the initial value of the radio button (with `init`)
  """

  def __init__(self, pd_lines=None, json=None):
    self.__pdpy__ = self.__class__.__name__
    if pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      pd_lines = pd_lines[4:]
      self.size   = self.__num__(pd_lines[0])
      self.flag   = self.__num__(pd_lines[1])
      self.init   = self.__pdbool__(pd_lines[2])
      self.number = self.__num__(pd_lines[3])
      self.comm = Comm(send=pd_lines[4], receive=pd_lines[5])
      self.label = IEMLabel(*pd_lines[6:11], pd_lines[13])
      self.bgcolor = self.__num__(pd_lines[11])
      self.fgcolor = self.__num__(pd_lines[12])
      self.value   = self.__num__(pd_lines[14])
    elif json is not None:
      super().__init__(json=json)
  
  def __pd__(self):
    """ Return the pd string for this object """
    s = str(self.size)
    s += f" {1 if self.flag else 0}"
    s += f" {1 if self.init else 0}"
    s += f" {self.number}"
    s += f" {self.comm.__pd__()}"
    s += f" {self.label.__pd__()}"
    s += f" {self.bgcolor}"
    s += f" {self.fgcolor}"
    s += f" {self.label.lbcolor}"
    s += f" {self.value}"
    return super().__pd__(s)
class Bng(PdObject):
  """
  The IEM Button Object
  =====================
  
  The IEM gui object is a IEM Bang button.

  1. 5: `size`: the size of the button
  2. 6: `hold`: time of the button on hold
  2. 7: `intrrpt`: the interruption time of the button
  2. 8: `init`: the init flag to trigger the button on loadtime
  3. 9: `send`: the sender symbol of the button
  3. 10: `receive`: the receiver symbol of the button
  4. 11-16: `IEMLabel` Parameters
  """
  

  def __init__(self, pd_lines=None, json=None):
    self.__pdpy__ = self.__class__.__name__
    if pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      pd_lines = pd_lines[4:]
      # log(1, "bng pd_lines: {}".format(pd_lines))
      self.size   = self.__num__(pd_lines[0])
      self.hold   = self.__num__(pd_lines[1])
      self.intrrpt= self.__num__(pd_lines[2])
      self.init   = self.__pdbool__(pd_lines[3])
      self.comm = Comm(send=pd_lines[4], receive=pd_lines[5])
      self.label = IEMLabel(*pd_lines[6:11], pd_lines[13])
      self.bgcolor = self.__num__(pd_lines[11])
      self.fgcolor = self.__num__(pd_lines[12])
    elif json is not None:
      super().__init__(json=json)
  
  def __pd__(self):
    """ Return the pd string for this object """
    s = str(self.size)
    s += f" {self.hold}"
    s += f" {self.intrrpt}"
    s += f" {1 if self.init else 0}"
    s += f" {self.comm.__pd__()}"
    s += f" {self.label.__pd__()}"
    s += f" {self.bgcolor}"
    s += f" {self.fgcolor}"
    s += f" {self.label.lbcolor}"
    return super().__pd__(s)
class Nbx(PdObject):
  """
  The IEM Number Box Object
  ==========================
  
  The IEM gui object is a IEM Number box (Number2).

  1. 5: `digits_width`: the width of the number box in digits.
  2. 6: `height`: the height of the numbers
  2. 7: `lower`: the lower limit of the number box range
  2. 8: `upper`: the upper limit of the number box range
  2. 9: `log_flag`: a flag to enable logarithmic value scaling
  2. 10: `init`: the init flag to trigger the number box on loadtime
  3. 11: `send`: the sender symbol of the number box
  3. 12: `receive`: the receiver symbol of the number box
  4. 13-18: `IEMLabel` Parameters
  5. 19: `value`: the initial value of the number box (with `init`)
  5. 20: `log_height`: upper limit of the log scale (with `log_flag`)
  """
  def __init__(self, pd_lines=None, json=None):
    self.__pdpy__ = self.__class__.__name__
    if pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      pd_lines = pd_lines[4:]
      self.digit_width = self.__num__(pd_lines[0])
      self.height   = self.__num__(pd_lines[1])
      self.limits = Bounds(*pd_lines[2:4])
      self.log_flag = self.__pdbool__(pd_lines[4])
      self.init    = self.__pdbool__(pd_lines[5])
      self.comm = Comm(send=pd_lines[6], receive=pd_lines[7])
      self.label = IEMLabel(*pd_lines[8:13], pd_lines[15])
      self.bgcolor = self.__num__(pd_lines[13])
      self.fgcolor = self.__num__(pd_lines[14])
      self.value = float(pd_lines[16])
      self.log_height = self.__num__(pd_lines[17])
    elif json is not None:
      super().__init__(json=json)
  
  def __pd__(self):
    """ Return the pd string for this object """
    s = str(self.digit_width)
    s += f" {self.height}"
    s += f" {self.limits.__pd__()}"
    s += f" {1 if self.log_flag else 0}"
    s += f" {1 if self.init else 0}"    
    s += f" {self.comm.__pd__()}"
    s += f" {self.label.__pd__()}"
    s += f" {self.bgcolor}"
    s += f" {self.fgcolor}"
    s += f" {self.label.lbcolor}"
    s += f" {self.value}"
    s += f" {self.log_height}"
    return super().__pd__(s)

class Slider(PdObject):
  """
  The IEM Slider Object
  =====================
  
  The IEM gui object is a IEM horizontal or vertical slider.
  The case of `vsl` or `hsl`

  1. 5: `width`: the width of the slider
  2. 6: `height`: the height of the slider
  2. 7: `lower`: the lower limit of the slider range
  2. 8: `upper`: the upper limit of the slider range
  2. 9: `log_flag`: a flag to enable logarithmic value scaling
  2. 10: `init`: the init flag to trigger the slider on loadtime
  3. 11: `send`: the sender symbol of the slider
  3. 12: `receive`: the receiver symbol of the slider
  4. 13-18: `:class:IEMLabel` Parameters
  5. 19: `value`: the initial value of the number box (with `init`)
  5. 20: `log_height`: upper limit of the log scale (with `log_flag`)
  """
  def __init__(self, pd_lines=None, json=None):
    self.__pdpy__ = self.__class__.__name__
    if pd_lines is not None:
      super().__init__(pd_lines=pd_lines[:4])
      pd_lines = pd_lines[4:]
      self.area = Size(*pd_lines[:2])
      self.limits = Bounds(*pd_lines[2:4])
      self.log_flag = self.__pdbool__(pd_lines[4])
      self.init    = self.__pdbool__(pd_lines[5])
      self.comm = Comm(send=pd_lines[6], receive=pd_lines[7])
      self.label = IEMLabel(*pd_lines[8:13], pd_lines[15])
      self.bgcolor = self.__num__(pd_lines[13])
      self.fgcolor = self.__num__(pd_lines[14])
      self.value = float(pd_lines[16])
      self.steady = self.__num__(pd_lines[17])
    elif json is not None:
      super().__init__(json=json)

  def __pd__(self):
    """ Return the pd string for this object """
    s = self.area.__pd__()
    s += f" {self.limits.__pd__()}"
    s += f" {1 if self.log_flag else 0}"
    s += f" {1 if self.init else 0}"
    s += f" {self.comm.__pd__()}"
    s += f" {self.label.__pd__()}"
    s += f" {self.bgcolor}"
    s += f" {self.fgcolor}"
    s += f" {self.label.lbcolor}"
    s += f" {self.value}"
    s += f" {1 if self.steady else 0}"
    return super().__pd__(s)
