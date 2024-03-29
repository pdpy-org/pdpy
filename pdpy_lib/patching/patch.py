#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
"""
Patch
=====
"""

import time
try:
  import pyaudio
  HAS_PYAUDIO = True
except ModuleNotFoundError:
  HAS_PYAUDIO = False
  print("You might want to get pyaudio: ``pip install pyaudio``")

try:
  import pylibpd
  HAS_PYLIBPD = True
except ModuleNotFoundError:
  HAS_PYLIBPD = False
  print("You might want to get libpd from https://github.com/libpd/libpd")

try:
    # On Linux dlopenflags need to be set for Pd plugin loading to work.
    import DLFCN
    import sys
    sys.setdlopenflags(DLFCN.RTLD_LAZY | DLFCN.RTLD_GLOBAL)
except ImportError:
    pass

from . import pdpy

__all__ = [ 'Patch' ]

class Patch(pdpy.PdPy):
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
  
  callback : :class:`bool`
    Run ``pyaudio`` in callback, non-blocking mode.
    This is useful for recording to disc.
    Set to ``False`` if you want live output (defaults: True).
  
  **kwargs:
    Other keyword arguments are passed to the :class:`pdpy.PdPy` base class


  Example
  -------

  First, we need to do our import::

    >>> import pdpy_lib as pdpy

  Now, make a patch with a ``name`` and set it to root, non-callback.

    >>> patch = pdpy.Patch(name='test', root=True, callback=False)
  
  Create some objects: an oscillator

    >>> osc = pdpy.Obj('osc~')
    >>> osc.addargs(440)
    <pdpy.Obj object at 0x106ac7850>
  
  Now, let's make a multiplier and a dac objects

    >>> mul = pdpy.Obj('*~')
    >>> mul.addargs(0.1)
    <pdpy.Obj object at 0x106729850>
    >>> dac = pdpy.Obj('dac~')

  Create the objects and connect them

    >>> patch.create(osc, mul, dac)
    <pdpy.Patch object at 0x106755640>
    >>> patch.connect(osc, mul)
    >>> patch.connect(mul, [dac, 0, 1])
  
  Write the patch

    >>> patch.write()
    Initialized Arranger graph placing algorithm.
  
  Start the audio and perform

    >>> patch.start_audio()
    <pyaudio.Stream object at 0x106ac74f0>
    >>> patch.perform()

  You should now hear a sinewave at 440 Hz.

  """
  def __init__(self, name=None, inch=2, outch=2, sr=44100, callback=False, **kwargs):
    """ Constructor """

    
    super().__init__(name, root = kwargs.pop('root', True), **kwargs)

    self.__callback__ = callback
    """ callback flag for pyaudio """
    
    self.__inch__ = inch
    """ input channels """

    self.__outch__ = outch
    """ output channels """
    
    self.__sr__ = sr
    """ sample rate """
    
    self.__tpb__ = 6
    """ ticks per buffer for pyaudio """
    
    self.__bs__ = pylibpd.libpd_blocksize() if HAS_PYLIBPD else 64
    """ libpd blocksize """
    
    self.__libpd__ = pylibpd.PdManager(
        self.__inch__, 
        self.__outch__, 
        self.__sr__,
        1
    ) if HAS_PYLIBPD else None
    """ The libpd manager class :class:`pylibpd.PdManager` """
    
    self.__pyaudio__ = pyaudio.PyAudio() if HAS_PYAUDIO else None
    """ The pyaudio class :class:`pyaudio.PyAudio` """

    self.__gui__ = False
    """ The flag if gui is on or off """

    self.__vis__ = False
    """ The flag if the root is vised or not """

  def __enter__(self):
    self.start_audio()
    return self
  
  def start_audio(self):
    """ Start the pyaudio stream """
    
    def _callback(in_data, frame_count, time_info, status):
      data = self.__libpd__.process(in_data) if HAS_PYLIBPD else in_data
      return (bytes(data), pyaudio.paContinue)
    
    self.__stream__ = self.__pyaudio__.open(
              format = pyaudio.paInt16,
              channels = min(self.__inch__, self.__outch__),
              rate = self.__sr__,
              input = True,
              output = True,
              frames_per_buffer = self.__bs__ * self.__tpb__, 
              stream_callback=_callback if self.__callback__ else None
    )
    """ the pyaudio stream """
    
    return self.__stream__

  def performCallback(self):
    """ Begin the audio stream loop in callback mode """
    self.__stream__.start_stream()
    while self.__stream__.is_active():
      time.sleep(0.1)
    self.__stream__.stop_stream()
  
  def perform(self):
    """ Begin the audio stream loop """

    while 1:
      data = self.__stream__.read(self.__bs__, exception_on_overflow=False)
      outp = self.__libpd__.process(data) if HAS_PYLIBPD else data
      self.__stream__.write(bytes(outp))
    
    self.__stream__.close()
  
  def __exit__(self, ctx_type, ctx_value, ctx_traceback):
    super().__exit__(ctx_type, ctx_value, ctx_traceback)

    if HAS_PYLIBPD: pylibpd.libpd_open_patch(self.patchname + '.pd')
    
    if HAS_PYAUDIO:
      if self.__callback__:
        try:
          self.performCallback()
        except Exception as e:
          raise Exception("There was an error", e)
      else:
        self.perform()
      
      self.__pyaudio__.terminate()
    
    if HAS_PYLIBPD: pylibpd.libpd_release()
  

  def start_gui(self, path=None):
    # pylibpd.libpd_init()
    pylibpd.libpd_init_audio(self.__inch__, self.__outch__, self.__sr__)
    pylibpd.libpd_subscribe('#py')
    pylibpd.libpd_set_message_callback(lambda x,y,z:print("MESSAGE",x,y,z))
    print_hook  = lambda x : print("CONSOLE", x) if x != '\n' else None
    pylibpd.libpd_set_print_callback(print_hook)
    # self.__instances__.append(pylibpd.libpd_new_instance())
    # pylibpd.libpd_set_instance(self.__instances__[-1])
    # [; pd dsp 1(
    # pylibpd.__libpd_start_message(1) # one entry in list
    # pylibpd.__libpd_add_float(1)
    # pylibpd.__libpd_finish_message("pd", "dsp")

    # self.__files__.append(pylibpd.libpd_openfile(self.name, '.'))

    # pylibpd.libpd_open_patch(self.name + '.pd')
    # failed = pylibpd.libpd_start_gui(self.__pdbin__.as_posix() + "/../..")
    if path is None:
      path = self.__pdpath__.as_posix() 
    
    failed = pylibpd.libpd_start_gui(path)
    
    if failed: print("gui startup failed")
    else: self.__gui__ = True
    self.poll()


  def stop_gui(self):
    if self.__gui__: pylibpd.libpd_stop_gui()
    print(pylibpd.libpd_exists("#py"))
    pylibpd.libpd_unsubscribe('#py')


  def send(self, recv, symbol, *args):
    pylibpd.libpd_message(recv, symbol, *args)
    self.poll()


  def poll(self):
    pylibpd.libpd_poll_gui()


  def create(self, *args):
    super().create(*args)


  def vis(self):
    if not self.__gui__: return

    if not self.__vis__:
      patch = self.patchname + '.pd'
      handle = 'pd-' + patch
      
      for line in self.as_list():
        # self.send(handle, *list(map(str, s.split(' ')))) # old mapping
        if line[0] == "#N":
          # donecanvasdialog / canvas creator
          pass
        elif line[0] == "#A":
          # array stuff
          pass
        elif line[0] == "#X":
          # object creator (on the last canvas)
          self.send(handle, *line[1:])
        else:
          pdpy.log(1, "What is this?", line)
      self.poll()
      self.__vis__ = True

  def start_patch(self):
    """ Start the Pd Patch """

    if not self.__gui__: return
    
    try:
      self.send('pd', 'menunew', self.patchname + '.pd', '.')
      self.poll()
    except Exception as e:
      pdpy.log(3, e)
