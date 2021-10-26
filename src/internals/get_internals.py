#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Get Pure Data internals """
import re, json

non = [
  r"\bbindlist",
  r"\bcanvasmaker",
  r"\bcanvas",
  r"\bmessage",
  r"\bmessresponder",
  r"\bclone\-inlet",
  r"\bclone\-outlet",
  r"\bexprproxy",
  r"\bgfxstsub",
  r"\bguiconnect",
  r"\blibpd_receive",
  r"\bobjectmaker",
  r"\bgatom",
  r"\bgfxstub",
  r"\blist\s\binlet",
]
obs = [
  r"\btemplate"
]

gen=[
  r"\bloadbang",
  r"\brandom|\buntil|\bclone",
]

time=[
  r"time|line",
  r"\bdelay",
  r"\bmakenote",
  r"\bmetro",
  r"\bpipe",
]
math=[
  r"\babs|atan|dbto|\brmstodb|\bdiv|\blog|\bmax|\bmin|\bmod|\bexp",
  r"\bcos|\bsin|\btan|\bpow|sqrt|\bwrap|\bftom|\bmtof|\bclip"
]
pdt = [
  r"\bfloat|\bsymbol|\bint|\bbang|\bpointer"
]
mid = [
  r"[a-z]{2}out$",
  r"[a-z]{2}in$",
  r"touch",
]
key = [
  r"key.*$",
]
flow = [
  r"\b[i|o].+let",
]
syst = [
  r"declare|print|control|file",
  r"\wpanel$",
  r"\wtime$",
]
gui = [
  r"\bcnv",
  r"\bnbx",
  r"\btgl",
  r"\bbng",
  r"\bvu",
  r"radio",
  r"sl",
  r"dl",
  r".+atom",
]
net = [
  r"send",
  r"receive",
]
ops = {
  "all":[
    r"^\W+$"
  ],
  "bin":[
    r"^\&$|^\|$|^\>\>$|^\<\<$"
  ],
  "math":[
    r"^[\*\%\+\-\/]$"
  ],
  "comp":[
    r"=|^\&\&$|^\<$|^\>$|^\|\|$"
  ]
}
dat = {
  "all": [
    r"^text.*|^array.*|\bscalar|qlist",
    r"save|tab|\bbag|\bpd|\bnamecanvas|\bvalue|\bpique"
  ],
  "canvas": [
    r"save|\bpd|\bnamecanvas"
  ],
  "array": [
    r"^array.*",
    r"tab|\bpique"
  ],
  "text": [
    r"^text.*|qlist"
  ],
  "struct": [
    r"\bscalar"
  ]
}
struct = [
  r"struct|polygon|curve|draw",
  r"get|set|plot|append|element"
]
prs = {
  "all" : [
    r"parse|format",
    r"^list.*",
    r"pack|route|sel|strip|trigger|\bpoly|change|spigot",
    r"\bmoses|\bchoice|\bswap",
  ],
  "list" : [
    r"^list.*",
    r"pack|strip",
    r"\bchoice|\bswap|\broute",
  ],
  "stream" : [
    r"sel|trigger|\bpoly|change",
    r"\bmoses|\bspigot",
  ],
  "format" : [ 
    r"parse|format",
  ]
}

sigmath = [
  r"\W\~",
  r"^abs|cos|sin|to|log|max|min|pow|sqrt|wrap|clip|exp"
]
sigfilt = [
  r"\_",
  r"zero|rev|biquad|lop|hip|vcf|^bp|pole|hilbert|complex"
]
sigfft = [
  r"fft"
]
sigarray = [
  r"tab"
]
sigroute = [
  r"catch|throw|^send|^receive"
]
sigdel = [
  r"del|^vd"
]
sigsys = [
  r"adc|dac|^write|^read|print|samplerate|pd"
]
siggen = [
  r"noise|^osc|phasor|loop"
]
ctrl2sig = [
  r"line|sig\~|^snapshot"
]
sigblock = [
  r"block|switch|bang|lrshift"
]

sigana = [
  r"env|hold|framp|bonk|bob|fiddle|sigmund"
]

def match(patterns, string):
  for pattern in patterns: 
    if re.search(pattern,string): return True
  return False



objects = {
  "signal": {
    "math":[],
    "fourier":[],
    "filters":[],
    "flow":[],
    "delays":[],
    "route":[],
    "generators":[],
    "system":[],
    "control_to_sig":[],
    "array":[],
    "block":[],
    "analysis":[],
  },
  "interface": {
    "midi":[],
    "keyboard":[],
    "system":[],
    "gui":[],
  },
  "operators": {
    "math":[],
    "binary":[],
    "comparison":[],
  },
  "data": {
    "array":[],
    "struct":[],
    "text":[],
    "canvas":[],
    "other":[],
  },
  "parsing": {
    "list":[],
    "stream":[],
    "format":[]
  },
  "control": {
    "flow":[],
    "network":[],
    "math":[],
    "time":[],
    "generators":[],
    "types":[],
  },
  "nonobj":[],
  "obsolete":[],
  "extra":[]
}

if "__main__" in __name__:
  import sys
  internals_file = sys.argv[1]
  internals_db = sys.argv[2]

  with open(internals_file, 'r') as fp:
    for obj in fp.readlines():
      obj = obj.strip()
      signal = objects['signal']
      control = objects['control']
      interface = objects['interface']
      operators = objects['operators']
      parsing = objects['parsing']
      data = objects['data']
      
      if re.search(r".\~",   obj): 
      
        if match(sigmath,    obj): signal['math'].append(obj)
        elif match(sigfft,   obj): signal['fourier'].append(obj)
        elif match(sigroute, obj): signal['route'].append(obj)
        elif match(sigdel,   obj): signal['delays'].append(obj)
        elif match(sigana,   obj): signal['analysis'].append(obj)
        elif match(sigsys,   obj): signal['system'].append(obj)
        elif match(siggen,   obj): signal['generators'].append(obj)
        elif match(sigblock, obj): signal['block'].append(obj)
        elif match(ctrl2sig, obj): signal['control_to_sig'].append(obj)
        elif match(sigfilt,  obj): signal['filters'].append(obj)
        elif match(sigarray, obj): signal['array'].append(obj)
        elif match(flow,     obj): signal['flow'].append(obj)
        else: 
          objects['extra'].append(obj)

      elif match(obs,  obj): objects['obsolete'].append(obj)
      elif match(non,  obj): objects['nonobj'].append(obj)
      
      elif match(mid,  obj): interface['midi'].append(obj)
      elif match(gui,  obj): interface['gui'].append(obj)
      elif match(key,  obj): interface['keyboard'].append(obj)
      elif match(syst,  obj): interface['system'].append(obj)
      
      elif match(struct, obj):          data['struct'].append(obj)
      
      elif match(dat['all'], obj):
        if match(dat['array'],    obj): data['array'].append(obj)
        elif match(dat['text'],   obj): data['text'].append(obj)
        elif match(dat['struct'], obj): data['struct'].append(obj)
        elif match(dat['canvas'], obj): data['canvas'].append(obj)
        else: 
          data['other'].append(obj)
      
      
      elif match(prs['all'], obj): 
        if match(prs['stream'],   obj): parsing['stream'].append(obj)
        elif match(prs['list'],   obj): parsing['list'].append(obj)
        elif match(prs['format'], obj): parsing['format'].append(obj)
        else: 
          objects['extra'].append(obj)
      
      elif match(flow, obj): control['flow'].append(obj)
      elif match(net,  obj): control['network'].append(obj)
      elif match(pdt,  obj): control['types'].append(obj)
      elif match(math, obj): control['math'].append(obj)
      elif match(gen,  obj): control['generators'].append(obj)
      elif match(time, obj): control['time'].append(obj)
          
      elif match(ops['all'], obj): 
        if match(ops['comp'],   obj): operators['comparison'].append(obj)
        elif match(ops['math'], obj): operators['math'].append(obj)
        elif match(ops['bin'],  obj): operators['binary'].append(obj)
        else: 
          operators['extra'].append(obj)
      
      
      else: 
        objects['extra'].append(obj)


  for kk, obj in objects.items():
    if isinstance(obj,dict):
      print(kk.upper())
      print("="*80)
      for k,v in obj.items():
        if isinstance(v,dict):
          print(k.upper())
          print("\t","."*71)
          for kk, vv in v.items():
            print("\t", kk.upper(),":", f"{len(vv)} objects")
            print("\t"*2, vv)
        else:
          print(k.upper(),":", f"{len(v)} objects")
          print(v)
        print("-"*80)

  with open(internals_db, "w") as fp:
    json.dump(objects, fp, indent=4)

