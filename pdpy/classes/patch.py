#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
"""
Patch
=====
"""

from .pdpy import PdPy
import pylibpd
from pyaudio import PyAudio, paInt16

__all__ = [ 'Patch' ]

class Patch(PdPy, pylibpd.PdManager, PyAudio):
  """ Patch interface to use pdpy and libpd

  Parameters
  ----------
  
  name : :class:`str` or ``None``
    Name for the patch
  
  inch : :class:`int`
    Number of input channels (defaults: 2)
  
  outch : :class:`int`
    Number of output channels (defaults: 2)
  
  sr : :class:`int`
    Sample rate (defaults: 44100)
  
  **kwargs:
    Other keyword arguments are passed to the :class:`pdpy.classes.pdpy.PdPy` base class


  Example
  -------

  First, we need to do our import::

    >>> import pdpy

  Now, make a patch with a ``name`` and set it to be the root patch.
    >>> patch = pdpy.Patch(name='test', root=True)
  
  Create some objects: an oscillator
    >>> osc = pdpy.Obj('osc~')
    >>> osc.addargs(440)
    <pdpy.classes.obj.Obj object at 0x106ac7850>
  
  Now, let's make a multiplier and a dac objects
    >>> mul = pdpy.Obj('*~')
    >>> mul.addargs(0.1)
    <pdpy.classes.obj.Obj object at 0x106729850>
    >>> dac = pdpy.Obj('dac~')

  Create the objects and connect them
    >>> patch.create(osc, mul, dac)
    <pdpy.classes.patch.Patch object at 0x106755640>
    >>> patch.connect(osc, mul)
    >>> patch.connect(mul, [dac, 0, 1])
  
  Write the patch
    >>> patch.write()
    Initialized Arrange graph placing algorithm.
  
  Start the audio and perform
    >>> patch.start_audio()
    <pyaudio.Stream object at 0x106ac74f0>
    >>> patch.perform()

  You should now hear a sinewave at 440 Hz.

  """
  def __init__(self, name=None, inch=2, outch=2, sr=44100, **kwargs):
    """ Constructor """
    
    PdPy.__init__(self, name, **kwargs)

    self.__inch__ = inch
    self.__outch__ = outch
    self.__sr__ = sr
    self.__bs__ = pylibpd.libpd_blocksize()
    self.__tpb__ = 6
    pylibpd.PdManager.__init__(self, self.__inch__, self.__outch__, self.__sr__, 1)
    
    PyAudio.__init__(self)

  def __enter__(self):
    self.start_audio()
    return self
  
  def start_audio(self):
    """ Start the pyaudio stream """
    self.__stream__ = self.open(
              format = paInt16,
              channels = min(self.__inch__, self.__outch__),
              rate = self.__sr__,
              input = True,
              output = True,
              frames_per_buffer = self.__bs__ * self.__tpb__)
    return self.__stream__
  
  def perform(self):
    """ Open the patch and begin the audio stream loop """
    pylibpd.libpd_open_patch(self.patchname + '.pd')
  
    while 1:
      data = self.__stream__.read(self.__bs__, exception_on_overflow=False)
      outp = self.process(data)
      self.__stream__.write(bytes(outp))


  def __exit__(self, ctx_type, ctx_value, ctx_traceback):
    super().__exit__(ctx_type, ctx_value, ctx_traceback)
  
    self.perform()
    self.__stream__.close()
    self.terminate()

    pylibpd.libpd_release()
  