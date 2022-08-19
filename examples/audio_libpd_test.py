#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
"""
Testing Audio with libpd
========================
"""

from pdpy import PdPy, Obj, Msg, Canvas
import pylibpd as libpd
import pyaudio
import random
patchname = "audio_libpd_test"
nchans = 2
partials = 42

p = pyaudio.PyAudio()
sr = 44100
tpb = 6
bs = libpd.libpd_blocksize()

with PdPy(name=patchname, root=True) as pd:

  # msg = Msg()
  # msg.addTarget('pd').add('dsp 1')
  # loadbang = Obj('loadbang')
  # pd.create(loadbang, msg)
  # pd.connect(loadbang, msg)
  
  startline = [
    Obj('loadbang'),
    Obj('del 10'),
    Msg('0.5 100'),
  ]
  pd.create(*startline)
  pd.connect(*startline)
  
  
  dac_channel = []
  
  for chan in range(nchans):
    channel_input = Obj('*~')
    lines = [
      Obj('line~'),
      channel_input,
      Obj('clip~').addargs(-0.707, 0.707),
      Obj('hip~').addargs(3),
      Obj('dac~').addargs(1 + chan) 
    ]
    dac_channel.append(channel_input[1])
    pd.create(*lines)
    pd.connect(startline[-1], *lines)
  
  
  for chan in range(nchans):
    for i in range(1, partials):
      objects = [
        Obj('osc~').addargs(random.random() * 0.1),
        Obj('*~').addargs(random.random() * 2 / i) ,
        Obj('+~') .addargs(random.random() * 1.75 * i + 65) ,
        Obj('mtof~'),
        Obj('osc~'),
        Obj('*~').addargs(2 / partials * (1-(i/partials))),
      ]
      pd.create(*objects)
      pd.connect(*objects, dac_channel[chan])
    
  pd.write("audio_libpd_test.json")
  pd.write()

stream = p.open(format = pyaudio.paInt16,
                channels = nchans,
                rate = sr,
                input = True,
                output = True,
                frames_per_buffer = bs * tpb)

m = libpd.PdManager(nchans, nchans, sr, 1)

# open patch
libpd.libpd_open_patch(patchname + '.pd')

while 1:
    data = stream.read(bs, exception_on_overflow=False)
    outp = m.process(data)
    stream.write(bytes(outp))

stream.close()
p.terminate()
libpd.libpd_release()
