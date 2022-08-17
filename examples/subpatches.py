#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
from pdpy import PdPy, Obj, Msg
import pylibpd as libpd
import pyaudio
import random
patchname = "subpatches"

with PdPy(name=patchname, root=True) as pd:

  lb = pd.createCanvas(name='loadbang')
  msg = Msg()
  msg.addTarget('pd').add('dsp 1')
  loadbang = Obj('loadbang')
  lb.create(loadbang, msg)
  lb.connect(loadbang, msg)
  
  dacout = pd.createCanvas(name='dacout')
  catcher = 'dacout'
  mainvol = Obj('*~') 
  mixer = [
    Obj('catch~').addargs(catcher),
    mainvol,
    Obj('clip~').addargs(-0.707, 0.707),
    Obj('dac~').addargs(1),
  ]
  line = [
    Obj('loadbang'),
    Obj('del 10'),
    Msg('0.8 100'),
    Obj('line~')
  ]
  dacout.create(*line, *mixer)
  dacout.connect(*mixer)
  dacout.connect(*line, mainvol[1])
  
  partials = 100
  

  for i in range(1, partials):
    subpatch = pd.createCanvas(name="oscil " + str(i))
    objects = [
      Obj('osc~').addargs(random.random() * 0.1),
      Obj('*~').addargs(random.random() * 2 / i) ,
      Obj('+~') .addargs(random.random() * 1.75 * i + 65) ,
      Obj('mtof~'),
      Obj('osc~'),
      Obj('*~').addargs(2 / partials * (1-(i/partials))),
      Obj('throw~').addargs(catcher)
    ]
    subpatch.create(*objects)
    subpatch.connect(*objects)
  
  pd.write("audio_libpd_test.json")
  pd.write()

p = pyaudio.PyAudio()
sr = 44100
tpb = 6
bs = libpd.libpd_blocksize()

stream = p.open(format = pyaudio.paInt16,
                channels = 1,
                rate = sr,
                input = True,
                output = True,
                frames_per_buffer = bs * tpb)

m = libpd.PdManager(1, 1, sr, 1)

# open patch
libpd.libpd_open_patch(patchname + '.pd')

# start dsp
libpd.libpd_compute_audio(1) 

while 1:
    data = stream.read(bs, exception_on_overflow=False)
    outp = m.process(data)
    stream.write(bytes(outp))

stream.close()
p.terminate()
libpd.libpd_release()
