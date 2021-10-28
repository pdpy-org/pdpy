#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
Pure Data Object Database creator 

this file works in conjunction with ./pddb.sh

"""


import re
import json
# from types import SimpleNamespace

def getkind(query, database, exact=False):
  """ Query a simple database for value key and subkey
  """
  if exact: 
    def compare(a,b): return a == b
  else: 
    def compare(a,b): return a in b
  
  for obj_kind, obj_subkind in database.items():
    matches = []
    if isinstance(obj_subkind, dict):
      for obj_subkinds, obj_names in obj_subkind.items():
        for obj_name in obj_names:
          if compare(query,obj_name):
            matches.append([obj_name, obj_kind, obj_subkinds])
    else:
      for obj_name in obj_subkinds:
          if compare(query,obj_name):
            matches.append([obj_name, obj_kind, obj_subkinds])
    if len(matches):
      return matches

def updateArray(array, name, dict):
  """ Converts one item lists into one items before dict update
  """
  array = list(filter(None,array))
  if len(array):
    if len(array) > 1: dict.update({name:array})
    else: dict.update({name:array[0]})

def gensym(s):
  """ Get the argument of Pure Data's `gensym()` function
  """
  symbols = re.findall(r"gensym\(\"(.*)\"\)", s)
  if len(symbols): return ' '.join(symbols)
  else: return symbols

def argparse(s, offset=5, last=-1):
  """ Disect C function arguments starting at `offset`, ending at `last`
  """
  s = s.split(',')
  s = s[offset:last]
  # gets rid of unnecessary spaces
  a = [ re.sub(' +',' ',i.strip()) for i in s]
  if len(a): return a

def getargs(x, tgt, offset=5):
  """ Get Pd's object or method arguments from their C-function calls
  """
  name = gensym(x)
  name = "float" if "ft1" in name else name
  yargs = argparse(x,offset=offset)
  if yargs is not None: tgt.append({ "name":name, "args":yargs })
  else: tgt.append(name)

def getnewmethod(s, tgt):
  """ Gets Pd's t_newmethod function name
  """
  s = s.split(',')
  a = ''
  if len(s)>1: a = re.sub(' +',' ',s[1].strip())
  if bool(a): tgt.append(a.replace('(t_newmethod)',''))

def parseIOlets(arr, patchable=False):
  """ Parse the newmethod function definition for the object iolets
  """
  
  iolets     = {'inlet':0,'outlet':0}
  sig_iolets = {'inlet':0,'outlet':0}


  for i in ' '.join(arr).replace('\n','').strip().split(";"):
    if "signalinlet_new"    in i: sig_iolets['inlet']  += 1
    elif "signaloutlet_new" in i: sig_iolets['outlet'] += 1
    elif "inlet_new"  in i: iolets['inlet']   += 1
    elif "outlet_new" in i: iolets['outlet']  += 1
  
  if patchable:
    iolets['inlet'] += 1

  # some obj (e.g. pipe) have variable iolets depending on arguments
  if iolets['inlet']>=4: iolets['inlet'] = "*"
  if iolets['outlet']>=4: iolets['outlet'] = "*"
  if sig_iolets['inlet']>=4: sig_iolets['inlet'] = "*"
  if sig_iolets['outlet']>=4: sig_iolets['outlet'] = "*"

  io = {}

  if iolets['inlet']:
    io.update({"inlets":iolets['inlet']})
  if iolets['outlet']:
    io.update({"outlets":iolets['outlet']})
  if sig_iolets['inlet']:
    io.update({"sig_inlets":sig_iolets['inlet']})
  if sig_iolets['outlet']:
    io.update({"sig_outlets":sig_iolets['outlet']})
  

  if bool(io):
    return {"iolets":io}

def getpatchable(s):
  """ Get the patchable flag on Pd's `class_new` call
  """
  s = s.split(',')
  return 4 < len(s) and '0' in s[4]

def parseSetup(arr, internals):
  """ Parse the object's `x_setup` call for object structure
  """
  name = ''
  
  for x in arr[0].split():
    if "_setup" in x: 
      name = " ".join(x.split("_")[:-1]).replace(' ','_')
  
  declarations = " ".join(arr[1:-1]).split("=")
  i=0
  obj = []
  
  for i in range(0,len(declarations)-1,2):
    methods = []
    arguments = []
    newmethod = []
    alias = []
    help = []
    signal = False
    patchable = False
    for x in declarations[i+1].replace("\n",'').split(";"):
      if   "class_new"    in x and "widget" not in x: 
        getargs(x,arguments)
        patchable = getpatchable(x)
        getnewmethod(x,newmethod)
      elif "help"         in x: help.append(gensym(x))
      elif "addcreator"   in x: alias.append(gensym(x))
      elif "addmethod"    in x or "set" in x: getargs(x,methods,3)
      elif "addbang"      in x or "set" in x: methods.append("bang")
      elif "addfloat"     in x or "set" in x: methods.append("float")
      elif "addsymbol"    in x or "set" in x: methods.append("symbol")
      elif "addpointer"   in x or "set" in x: methods.append("pointer")
      elif "addlist"      in x or "set" in x: methods.append("list")
      elif "addanything"  in x or "set" in x: methods.append("any")
      elif "MAINSIGNALIN" in x: signal=True
      else: continue
    
    if "dsp" in methods: signal = True

    o = {}
    
    if signal: o.update({'signal': signal})
    if patchable: o.update({'patchable': patchable})
    updateArray(alias, 'alias', o)
    updateArray(help, 'help', o)
    updateArray(newmethod, 'newmethod', o)
    updateArray(arguments, 'arguments', o)
    if signal and 'dsp' in methods: methods.pop(methods.index('dsp'))
    updateArray(methods, 'methods', o)

    if o:
      kind = ''
      if 'arguments' in o:
        if isinstance(o['arguments'],dict):
          nn = o['arguments']['name']
          if bool(nn):
            kind = getkind(nn, internals, exact=True)
        else:
          kind = getkind(o['arguments'], internals, exact=True)

        if bool(kind):
          o['description'] = {
            "kind": kind[0][1],
            "subkind": kind[0][2],
          }
            # updateArray(kind, "description", o)
      # else: print('no arguments', o)
      obj.append(o)
      # if 'newmethod' in o and o['newmethod'] == "0": name = False
      # else: obj.append(o)
  
  if len(obj) == 1: obj = obj[0]
  
  if bool(name):
    return {
      "className": name,
      "attributes": obj
    }



if "__main__" in __name__:
  import sys
  
  arguments_file = sys.argv[1]
  internals_file = sys.argv[2]
  pddb_file      = sys.argv[3]
  
  args = []
  internals = {}
  fargs = []

  with open(arguments_file,"r") as fp:
    for i in fp.readlines():
      a = i.split(':')
      if 1 < len(a) and a[1] != "\n":
        args.append({"file":a[0],"lines":[int(i) for i in a[1].split()]})

  with open(internals_file,"r") as f:
    internals = json.load(f)
    # internals = json.load(f, object_hook=lambda d:SimpleNamespace(**d))

  # private_classes = [] # ["m_class.c", "s_loader.c", "g_text.c"]

  for i,o in enumerate(args):
    # if o['file'].split("/")[-1] in private_classes: continue
    file = open(o['file'],'r')
    flines = file.readlines()
    data = []
    prevend = 0
    for line in o['lines']:
      # get line range between _setup() and end curly bracket
      begin = line
      while begin > 0 and "_setup" not in flines[begin]:
        begin -= 1

      end = line + 1
      while end < len(flines) and "}\n" not in flines[end]:
        end += 1
      
      if begin < prevend: 
        continue
      else: 
        line_range = flines[begin:end]
        prevend = end
        if "/*" in line_range and "*/" in line_range: continue
        classDefinition = parseSetup(line_range, internals)
        if classDefinition is not None:
          data.append(classDefinition)

    o.update({'classes':data})

    if 'classes' in o: 
      # clone the object to get a fresh linenum-free copy
      myobj = {'file': o['file'], 'classes':o['classes']}
      
      # for every class in this file
      for c in myobj['classes']:
        # print(c)
        cname = c['className']
        pd_new = f"pd_new({cname}"
        #is signal obj
        signal = 'attributes' in c and 'signal' in c['attributes']
        patchable = None
        if 'attributes' in c and 'patchable' in c['attributes']:
          patchable = c['attributes']['patchable']
        in_out_lets = []
        
        # get index of newmethod definition
        pd_new_idx = None
        for i, line in enumerate(flines):
          if "/*" in line or "*/" in line: continue
          if pd_new in line:
            pd_new_idx = i
            break
        
        # advance from new_method index until bracket close
        prevend = 0
        if pd_new_idx is not None:
          end = pd_new_idx + 1
          while end < len(flines) and "return" not in flines[end]:
            end += 1

        # parse the new method definition for iolets
        if pd_new_idx:

          iolets = parseIOlets(flines[pd_new_idx:end], patchable=patchable)
          if iolets: 
            if isinstance(c['attributes'],list):
              for y in c['attributes']:
                y.update(iolets)
            else:
              c['attributes'].update(iolets)
      
      fargs.append(myobj)

    file.close()

  with open(pddb_file, "w") as f:
    json.dump(fargs, f, indent=4)
