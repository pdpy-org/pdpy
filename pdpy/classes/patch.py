#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
from .pdpy import PdPy
import pylibpd
from pyaudio import PyAudio, paInt16

__all__ = [ 'Patch' ]

class Patch(PdPy, pylibpd.PdManager, PyAudio):
  
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
    self.__stream__ = self.open(
                format = paInt16,
                channels = min(self.__inch__, self.__outch__),
                rate = self.__sr__,
                input = True,
                output = True,
                frames_per_buffer = self.__bs__ * self.__tpb__)
    return self
  
  def __exit__(self, ctx_type, ctx_value, ctx_traceback):
    super().__exit__(ctx_type, ctx_value, ctx_traceback)
    pylibpd.libpd_open_patch(self.patchname + '.pd')
    
    while 1:
      data = self.__stream__.read(self.__bs__, exception_on_overflow=False)
      outp = self.process(data)
      self.__stream__.write(bytes(outp))

    self.__stream__.close()
    self.terminate()

    pylibpd.libpd_release()
  