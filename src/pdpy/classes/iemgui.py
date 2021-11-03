#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Class Definitions """

# from ..util.utils import  log
from .base import Base
from .default import PdFonts
from .classes import Base, Point, Size, Bounds

__all__ = [  "IEMLabel", "PdIEMGui" ]

class PdFont(Base):
  def __init__(self, face, size):
    self.__pdpy__ = self.__class__.__name__
    self.face = self.num(face)
    self.name = PdFonts[self.face if self.face < len(PdFonts) else -1]
    self.size = self.num(size)

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
  def __init__(self, label, xoff, yoff, fface, fsize, lbcolor):
    self.__pdpy__ = self.__class__.__name__
    self.label = None if "empty" == label else label
    self.offset = Point(xoff, yoff)
    self.font = PdFont(fface, fsize)
    self.lbcolor = self.num(lbcolor)

# end of class IEMLabel --------------------------------------------------------

class PdIEMGui(IEMLabel):
  """ 
  The IEM GUI Object
  ==================
  
  Description
  -----------
  This is the IEM gui object class that represents and iemgui.

  Initialization Arguments
  ------------------------
  1. `id`: the id of the object
  2. `x`: the x-position of the object
  3. `y`: the y-position of the object
  4. `className`: the class name of the gui object.
  
  The IEMLabel is created in accordance with `className`

  Methods
  -------

  - :func:`PdIEMGui.createVu`
  - :func:`PdIEMGui.createToggle`
  - :func:`PdIEMGui.createCnv`
  - :func:`PdIEMGui.createRadio`
  - :func:`PdIEMGui.createBng`
  - :func:`PdIEMGui.createNbx`
  - :func:`PdIEMGui.createSlider`

  """

  def __init__(self, *argv):
    self.__pdpy__ = self.__class__.__name__
    self.id = argv[0]
    self.position = Point(*argv[1:3])
    # check if argument 3 is present in argv
    if 3 < len(argv):
      self.className = argv[3]
      if 4 < len(argv):
        self.createGui(argv[4:])
  
  def createGui(self, args):
    """ 
    The IEMGUI creator
    --------------------
    
    This creator checks agains the `className` and calls the appropriate
    creator function.

    """
    args = list(args)
    if "vu" in self.className:
      self.createVu(args)
    elif "tgl" in self.className:
      self.createToggle(args)
    elif "cnv" in self.className or "my_canvas" in self.className:
      self.createCnv(args)
    elif "radio" in self.className or "rdb" in self.className:
      self.createRadio(args)
    elif "bng"    in self.className:
      self.createBng(args)
    elif "nbx"    in self.className:
      self.createNbx(args)
    elif "sl" in self.className:
      self.createSlider(args)
    else:
      raise ValueError("Unknown class name: {}".format(self.className))
  
  # end of createGui method ---------------------------------------------------

  def createVu(self, args):
    """
    The case of `vu`
    --------------------
    
    The IEM gui object is a vu meter.

    1. 5: `width`: the width of the vu meter area
    2. 6: `height`: the height of the vu meter area
    3. 7: `receive`: the receiver symbol of the vu meter
    4. 8-13: `IEMLabel` Parameters
    5. 14: `scale`: flag to draw the dB scale or not
    6. 15: `flag`: another flag.
    """
    args = list(args)
    self.area = Size(*args[:2])
    self.receive = args[2]
    super().__init__(*args[3:8], args[9])
    self.bgcolor = self.num(args[8])
    self.scale= self.pdbool(args[10]) if 10 < len(args) else None
    self.flag = self.pdbool(args[11]) if 11 < len(args) else None
  
  # end of createVu method -----------------------------------------------------

  def createToggle(self, args):
    """
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
    args = list(args)
    self.size = self.num(args[0])
    self.init = self.pdbool(args[1])
    self.send = args[2] if args[2] != "empty" else None
    self.receive = args[3] if args[3] != "empty" else None
    super().__init__(*args[4:9], args[11])
    self.bgcolor = self.num(args[9])
    self.fgcolor = self.num(args[10])
    self.flag    = self.num(args[12])
    self.nonzero = self.num(args[13])
  
  # end of createToggle method ------------------------------------------------

  def createCnv(self, args):
    """
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
    args = list(args)
    self.size = self.num(args[0])
    self.area = Size(*args[1:3])
    if 12 < len(args):
      self.send = args[3] if args[3] != "empty" else None
      off = 0
    else:
      off = 1
    self.receive = args[4-off]  if args[4-off] != "empty" else None
    super().__init__(*args[5-off:10-off], args[11-off])
    self.bgcolor = self.num(args[10-off])
    self.flag    = self.num(args[12-off])
  
  # end of createCnv method ---------------------------------------------------

  def createRadio(self, args):
    """
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
    args = list(args)
    self.size   = self.num(args[0])
    self.flag   = self.num(args[1])
    self.init   = self.pdbool(args[2])
    self.number = self.num(args[3])
    self.send    = args[4] if args[4] != "empty" else None
    self.receive = args[5] if args[5] != "empty" else None
    super().__init__(*args[6:11], args[13])
    self.bgcolor = self.num(args[11])
    self.fgcolor = self.num(args[12])
    self.value   = self.num(args[14])
  
  # end of createRadio method -------------------------------------------------

  def createBng(self, args):
    """
    The case of `bng`
    --------------------
    
    The IEM gui object is a IEM Bang button.

    1. 5: `size`: the size of the button
    2. 6: `hold`: time of the button on hold
    2. 7: `intrrpt`: the interruption time of the button
    2. 8: `init`: the init flag to trigger the button on loadtime
    3. 9: `send`: the sender symbol of the button
    3. 10: `receive`: the receiver symbol of the button
    4. 11-16: `IEMLabel` Parameters
    """
    args = list(args)
    self.size   = self.num(args[0])
    self.hold   = self.num(args[1])
    self.intrrpt= self.num(args[2])
    self.init   = self.pdbool(args[3])
    self.send    = args[4] if args[4] != "empty" else None
    self.receive = args[5] if args[5] != "empty" else None
    super().__init__(*args[6:11], args[13])
    self.bgcolor = self.num(args[11])
    self.fgcolor = self.num(args[12])
  
  # end of createBng method ---------------------------------------------------

  def createNbx(self, args):
    """
    The case of `nbx`
    --------------------
    
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
    args = list(args)
    self.digit_width = self.num(args[0])
    self.height   = self.num(args[1])
    self.limits = Bounds(*args[2:4])
    self.log_flag = self.pdbool(args[4])
    self.init    = self.pdbool(args[5])
    self.send    = args[6] if args[6] != "empty" else None
    self.receive = args[7] if args[7] != "empty" else None
    super().__init__(*args[8:13], args[15])
    self.bgcolor = self.num(args[13])
    self.fgcolor = self.num(args[14])
    self.value = float(args[16])
    self.log_height = self.num(args[17])

  # end createNbx method ------------------------------------------------------

  def createSlider(self, args):
    """
    The case of `vsl` or `hsl`
    --------------------
    
    The IEM gui object is a IEM horizontal or vertical slider.

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
    args = list(args)
    self.area = Size(*args[:2])
    self.limits = Bounds(*args[2:4])
    self.log_flag = self.pdbool(args[4])
    self.init    = self.pdbool(args[5])
    self.send    = args[6] if args[6] != "empty" else None
    self.receive = args[7] if args[7] != "empty" else None
    super().__init__(*args[8:13], args[15])
    self.bgcolor = self.num(args[13])
    self.fgcolor = self.num(args[14])
    self.value = float(args[16])
    self.steady = self.num(args[17])

  # end of createSlider method ------------------------------------------------

# end of class IEMGuiObject ---------------------------------------------------