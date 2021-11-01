#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Routines to get pdpy elements back onto pd-formatted string """

from ..util.utils import log
from ..classes.default import GOPArrayFlags

__all__=[
  "getStruct", "getCanvas", "getDependencies", "getNodes", "getComments", "getCoords", "getConnections", "getRestore"
]

# **************************************************************************** #
# some globals
# **************************************************************************** #

# Flag to indicate if we are in an object
isobj = True

# This is a list that holds the depth of the current object
depth = []

# This is a dictionary with 
# - the node indices as keys, and 
# - the last depth index as values
obj_map = {}

# **************************************************************************** #
# Routines to keep track of object connections
# **************************************************************************** #

def map_idx(id):
  """ Maps a node id to a unique index """
  # get the depth and obj_map globals
  global depth
  global obj_map
  # increment the last depth index by one
  depth[-1] += 1
  # add the node to the map
  obj_map.update({ id : depth[-1] })

def remap(id):
  """ Get the value from the mapped indices """
  # get the object map
  global obj_map
  s = '-1'
  try:
    # query the map for the value at the id key
    s = str( obj_map[int(id)] )
  except KeyError:
    # if the key is not found, log the error
    log(1, "remap()::Key Not Found", id)
    print(obj_map)
  finally:
    # return the value
    return s

# **************************************************************************** #
# TODO: Define a custom decoder
# **************************************************************************** #

# def PdPyDecoder(obj):
#   if "__type__" in obj and obj["__type__"] == "PdPy":
#     o = PdPy(obj["patchname"], obj["encoding"])
#   else:
#     return lambda d: SimpleNamespace(**d)

# **************************************************************************** #
# Helper to get the property of an object
# **************************************************************************** #

def get(obj, prop, subprop=None, default=None):

  if isinstance(obj, dict) or isinstance(obj, list):
    o = obj[prop]
  else:
    o = getattr(obj, str(prop))
  
  if subprop is None:
    return o if o is not None else default
  else:
    return get(o, subprop)

# **************************************************************************** #
# Routines to get data from structured pdpy json file into pd-formatted string
# **************************************************************************** #

def getStruct(obj, out):
  """ Parses the struct entry into pd-lingo 
  
  Description
  -----------  
    This function takes a python object `obj` (coming from json),
    and an `out` list. 
  
  It returns `None`, but they append pd-formatted strings to the `out` list
  
  """
  if hasattr(obj, 'struct'):
    for d in get(obj,'struct'):
      s = f"#N struct {get(d,'name')}"

      if hasattr(d, 'float'):
        s += ' '
        s += ' '.join([ f"float {x}" for x in get(d,'float') ])
      
      if hasattr(d, 'symbol'):
        s += ' '
        s += ' '.join([ f"symbol {x}" for x in get(d,'symbol') ])
      
      if hasattr(d, 'text'):
        s += ' '
        s += ' '.join([ f"text {x}" for x in get(d,'text') ])
      
      if hasattr(d, 'array'):
        s += ' '
        s += ' '.join([ f"array {get(x,'name')} {get(x,'template')}" for x in get(d,'array') ])
      
      out.append(s + ";\r\n")

def getComments(obj, out):
  """ Parses the comment entry into pd-lingo 
  
  Description
  -----------  
    This function takes a python object `obj` (coming from json),
    and an `out` list. 
  
  It returns `None`, but they append pd-formatted strings to the `out` list
  
  """

  if hasattr(obj, 'comments'):
    for x in get(obj,'comments'):
      s = "#X text"
      s += f" {str(get(x,'position','x'))} {str(get(x,'position','y'))} "
      if len(get(x,'text')) == 1: s += get(x, 'text', 0)
      else: s += ' '.join([ f"{t} \\;" for t in get(x,'text') ])
      s = s.replace(',',' \,')
      if hasattr(x, 'border'): s += f", f {str(get(x,'border'))}"
      out.append(s + ";\r\n")

def getConnections(obj, out):
  """ Parses the connections entry into pd-lingo 
  
  Description
  -----------  
    This function takes a python object `obj` (coming from json),
    and an `out` list. 
  
  It returns `None`, but they append pd-formatted strings to the `out` list
  
  """
  if hasattr(obj, 'edges'):
    for x in get(obj,'edges'):
      s = "#X connect"
      s += f" {remap(get(x,'source','id'))} {str(get(x,'source','port'))}"
      s += f" {remap(get(x,'sink','id'))} {str(get(x,'sink','port'))}"
      if '-1' not in s:
        out.append(s + ";\r\n")
      else:
        log(1,"EDGES", x)
        log(1,"Missed a connection:", s)


def getNodes(obj, out):
  """ Parses the nodes entry into pd-lingo 
  
  Description
  -----------  
    This function takes a python object `obj` (coming from json),
    and an `out` list. 
  
  It returns `None`, but they append pd-formatted strings to the `out` list
  
  """
  # uncomment this to add a comment offset
  # c_offset =  len(get(obj,'comments'))-1 if hasattr(obj, 'comments') else 0
  c_offset = 0
  
  if hasattr(obj, 'nodes'):
    haso = False
    for x in obj.nodes:
      s = ''
      
      # If the node has an ID, get it and use it to update the object map
      if hasattr(x,"id"):
        # update the object map
        map_idx(int(get(x,'id'))-c_offset)
        # uncomment to see the mapping on the pd-file
        # s += ' ' + str(obj_map[get(x,'id')]) + ' '
 
      if get(x, "__pdpy__") == "Canvas":
        # uncomment to see the mapping on the pd-file
        # out.append(str(obj_map[get(x,'id')]) + ' ')
        getCanvas(x, out)
      elif not hasattr(x, 'className'):
        if get(x, "__pdpy__") == "PdObject":
          s += "#X obj"
          s += ' ' + str(get(x,'position','x'))
          s += ' ' + str(get(x,'position','y'))
        else:
          log(1,"WARNING, UNPARSED", x)
      else:
        
        if get(x, "__pdpy__") == "PdMessage":
        
          s += '#X msg'
          s += ' ' + str(get(x,'position','x'))
          s += ' ' + str(get(x,'position','y'))
        
          if hasattr(x, "targets"):
        
            for t in get(x,'targets'):
        
              if 'outlet' == get(t,'address'):
                msg = get(t,'message')
                s += ' ' + ' \\, '.join(msg)
        
              else:
                s += ' \\; ' + get(t,'address') + ' ' + ' \\, '.join(get(t,'message'))
        
        elif get(x, "__pdpy__") == "Scalar":
        
          s += "#X scalar"
          s += ' ' + get(x,'name')
        
          for e in get(x,'data'):
            s += ' ' + ' '.join(e) + " \;"
        
        elif get(x, "__pdpy__") == "PdNativeGui":
        
          s += getNativeGui(x, get(x,'className'))
        
        elif "goparray" == get(x,'className'):
        
          s += "#X array"
          s += ' ' + get(x,'name')
          s += ' ' + str(get(x,'size'))
          s += ' float'
          s += ' ' + str(GOPArrayFlags.index(get(x,'flag')))
        
        else:
        
          # TODO
          # IEMGUI stuff
          # more granular control on each param
          className = get(x,'className')
          s += "#X obj"
          s += ' ' + str(get(x,'position','x'))
          s += ' ' + str(get(x,'position','y'))
          s += ' ' + className
          
          if get(x, "__pdpy__") == 'PdIEMGui':
            # log(1,x)
            # s += ' ' + ' '.join(get(x,'args'))
            
            rcv = get(x,'receive') if hasattr(x,'receive') else 'empty'
            snd = get(x,'send') if hasattr(x,'send') else 'empty'
            lbl = get(x,'label') if hasattr(x,'label') else 'empty'
            xof = str(get(x,'offset', 'x')) if hasattr(x,'offset') else None
            yof = str(get(x,'offset', 'y')) if hasattr(x,'offset') else None
            lff = str(get(x,'font', 'face')) if hasattr(x,'font') else None
            lfs = str(get(x,'font', 'size')) if hasattr(x,'font') else None
            lbc = str(get(x,'lbcolor')) if hasattr(x,'lbcolor') else None
            bgc = str(get(x,'bgcolor')) if hasattr(x,'bgcolor') else None
            fgc = str(get(x,'fgcolor')) if hasattr(x,'fgcolor') else None

            if "vu" == className:
              s+=f" {str(get(x,'area','width'))} {str(get(x,'area','height'))}"
              s+=f" {rcv} {lbl}"
              s+=f" {'-1' if xof is None else xof}"
              s+=f" {'-8' if yof is None else yof}"
              s+=f" {'0' if lff is None else lff}"
              s+=f" {'10' if lfs is None else lfs}"
              s+=f" {'-66577' if bgc is None else bgc}"
              s+=f" {'-1' if lbc is None else lbc}"
              if hasattr(x,'scale'):
                s+=f" {'1' if get(x,'scale') else '1'}"
              else:
                s+= ' 1'
              if hasattr(x,'flag'):
                s+=f" {'1' if get(x,'flag') else '0'}"
              else:
                s+= ' 0'
            
            elif "tgl" == className:
              # log(1,"TGL",x)
              s+=f" {str(get(x,'size'))}"
              s+=f" {'1' if get(x,'init') else '0'}"
              s+=f" {snd} {rcv} {lbl}"
              s+=f" {'17' if xof is None else xof}"
              s+=f" {'7' if yof is None else yof}"
              s+=f" {'0' if lff is None else lff}"
              s+=f" {'10' if lfs is None else lfs}"
              s+=f" {'-262144' if bgc is None else bgc}"
              s+=f" {'-1' if fgc is None else fgc}"
              s+=f" {'-1' if lbc is None else lbc}"
              s+=f" {'1' if get(x,'flag') else '0'}"
              s+=f" {str(get(x,'nonzero',default='1'))}"
              # log(1,s)

            elif "cnv" == className or "my_canvas" == className:
              s+=f" {str(get(x,'size',default='15'))}"
              s+=f" {str(get(x,'area','width'))} {str(get(x,'area','height'))}"
              s+=f" {snd} {rcv} {lbl}" if snd is not None else f" {rcv} {lbl}"
              s+=f" {'20' if xof is None else xof}"
              s+=f" {'12' if yof is None else yof}"
              s+=f" {'0' if lff is None else lff}"
              s+=f" {'14' if lfs is None else lfs}"
              s+=f" {'-233017' if bgc is None else bgc}"
              s+=f" {'-66577' if lbc is None else lbc}"
              s+=f" {'1' if get(x,'flag') else '0'}"

            elif "radio" in className or 'rdb' == className:
              s+=f" {str(get(x,'size'))} {str(get(x,'flag'))}"
              s+=f" {'1' if get(x,'init') else '0'} {str(get(x,'number'))}"
              s+=f" {snd} {rcv} {lbl}"
              s+=f" {'0' if xof is None else xof}"
              s+=f" {'-8' if yof is None else yof}"
              s+=f" {'0' if lff is None else lff}"
              s+=f" {'10' if lfs is None else lfs}"
              s+=f" {'-262144' if bgc is None else bgc}"
              s+=f" {'-1' if fgc is None else fgc}"
              s+=f" {'-1' if lbc is None else lbc}"
              s+=f" {str(get(x,'value'))}"

            elif "bng" == className:
              s+=f" {str(get(x,'size'))} {str(get(x,'hold'))}"
              s+=f" {str(get(x,'intrrpt'))} {'1' if get(x,'init') else '0'}"
              s+=f" {snd} {rcv} {lbl}"
              s+=f" {'17' if xof is None else xof}"
              s+=f" {'7' if yof is None else yof}"
              s+=f" {'0' if lff is None else lff}"
              s+=f" {'10' if lfs is None else lfs}"
              s+=f" {'-262144' if bgc is None else bgc}"
              s+=f" {'-1' if fgc is None else fgc}"
              s+=f" {'-1' if lbc is None else lbc}"

            elif "nbx" == className:
              s+=f" {str(get(x,'digit_width'))} {str(get(x,'height'))}"
              s+=f" {str(get(x,'limits', 'lower'))}"
              s+=f" {str(get(x,'limits', 'upper'))}"
              s+=f" {'1' if get(x,'log_flag') else '0'} {'1' if get(x,'init') else '0'}"
              s+=f" {snd} {rcv} {lbl}"
              s+=f" {'0' if xof is None else xof}"
              s+=f" {'-8' if yof is None else yof}"
              s+=f" {'0' if lff is None else lff}"
              s+=f" {'10' if lfs is None else lfs}"
              s+=f" {'-262144' if bgc is None else bgc}"
              s+=f" {'-1' if fgc is None else fgc}"
              s+=f" {'-1' if lbc is None else lbc}"
              s+=f" {str(get(x,'value'))}"
              s+=f" {str(get(x,'log_height'))}"
            
            elif "hsl" == className:
              s+=f" {str(get(x,'area','width'))} {str(get(x,'area','height'))}"
              s+=f" {str(get(x,'limits', 'lower'))}"
              s+=f" {str(get(x,'limits', 'upper'))}"
              s+=f" {'1' if get(x,'log_flag') else '0'}"
              s+=f" {'1' if get(x,'init') else '0'}"
              s+=f" {snd} {rcv} {lbl}"
              s+=f" {'-2' if xof is None else xof}"
              s+=f" {'-8' if yof is None else yof}"
              s+=f" {'0' if lff is None else lff}"
              s+=f" {'10' if lfs is None else lfs}"
              s+=f" {'-262144' if bgc is None else bgc}"
              s+=f" {'-1' if fgc is None else fgc}"
              s+=f" {'-1' if lbc is None else lbc}"
              s+=f" {str(get(x,'value'))}"
              s+=f" {'1' if get(x,'steady') else '0'}"
            
            elif "vsl" == className:
              s+=f" {str(get(x,'area','width'))} {str(get(x,'area','height'))}"
              s+=f" {str(get(x,'limits', 'lower'))}"
              s+=f" {str(get(x,'limits', 'upper'))}"
              s+=f" {'1' if get(x,'log_flag') else '0'} {'1' if get(x,'init') else '0'}"
              s+=f" {snd} {rcv} {lbl}"
              s+=f" {'0' if xof is None else xof}"
              s+=f" {'-9' if yof is None else yof}"
              s+=f" {'0' if lff is None else lff}"
              s+=f" {'10' if lfs is None else lfs}"
              s+=f" {'-262144' if bgc is None else bgc}"
              s+=f" {'-1' if fgc is None else fgc}"
              s+=f" {'-1' if lbc is None else lbc}"
              s+=f" {str(get(x,'value'))}"
              s+=f" {'1' if get(x,'steady') else '0'}"
            
            else:
              log(2,"Can't parse PdIEMGui", x)

          
          else:
            
            if hasattr(x, "subclass"):
              s += ' ' + get(x,'subclass')
            
            if hasattr(x, "keep"):
              if get(x,'keep'):
                s += ' -k' 

            if hasattr(x, "name"):
              s += ' ' + get(x,'name')
            
            if hasattr(x, "size"):
              s += ' ' + str(get(x,'size'))

            if hasattr(x, "data"):
              haso = True
              
            if hasattr(x,"args"):
              args = get(x,'args')
              # print("ARGUMENTS",args,type(args))
              if isinstance(args, list):
                s += ' ' + ' '.join(args)
              else:
                s += args
        
        out.append(s + ";\r\n")
        getBorder(x, out)  

      if haso:
        
        s = "#A"
        
        if "text" == get(x,'className'):
          s += ' set'
        else:
          s += ' saved'
        
        for e in get(x,'data'):
        
          if isinstance(e, str):
            s += ' ' + e #+ " \\;"
        
          elif isinstance(e, list):
            s += ' ' + ' '.join(e) + " \\;"
        
          else:
            s += ' ' + str(e)
        
        out.append(s + ";\r\n")
        haso = False

def getDeclare(obj, out, kind):
  """ Parses the declare entry into pd-lingo 
  
  Description
  -----------  
    This function takes a python object `obj` (coming from json),
    and an `out` list. 
  
  It returns `None`, but they append pd-formatted strings to the `out` list
  
  """
  if hasattr(obj, kind):
    s = "#X declare"
    for x in get(obj, kind):
      s += f" -{kind[:-1]} {x}"
    out.append(s + ";\r\n")

def getDependencies(obj, out):
  """ Parses the dependencies entry into paths and libs using `getDeclare()` """
  if hasattr(obj, "dependencies"):
    getDeclare(get(obj,'dependencies'), out, 'paths')
    getDeclare(get(obj,'dependencies'), out, 'libs')

def getRestore(obj, out):
  """ Parses the restore entry into pd-lingo 
  
  Description
  -----------  
    This function takes a python object `obj` (coming from json),
    and an `out` list. 
  
  It returns `None`, but they append pd-formatted strings to the `out` list
  
  """
  # Get the depth and remove the last element
  global depth
  depth.pop()
  
  if hasattr(obj, 'position'):
    s = '#X restore'
    s += ' ' + str(get(obj,'position','x'))
    s += ' ' + str(get(obj,'position','y'))
    s += ' ' + get(obj,'title')
    out.append(s + ";\r\n")

def getBorder(obj, out):
  """ Parses the border entry into pd-lingo 
  
  Description
  -----------  
    This function takes a python object `obj` (coming from json),
    and an `out` list. 
  
  It returns `None`, but they append pd-formatted strings to the `out` list
  
  """
  if hasattr(obj, 'border'):
    out.append(f"#X f {str(get(obj,'border'))} ;\r\n")

def getCoords(obj, out):
  """ Parses the coords entry into pd-lingo 
  
  Description
  -----------  
    This function takes a python object `obj` (coming from json),
    and an `out` list. 
  
  It returns `None`, but they append pd-formatted strings to the `out` list
  
  """
  if hasattr(obj, 'coords'):
    s = '#X coords'
    s += ' ' + str(get(get(obj,'coords','range'),'a','x'))
    s += ' ' + str(get(get(obj,'coords','range'),'b','x'))
    s += ' ' + str(get(get(obj,'coords','range'),'a','y'))
    s += ' ' + str(get(get(obj,'coords','range'),'b','y'))
    s += ' ' + str(get(get(obj,'coords','dimension'),'width'))
    s += ' ' + str(get(get(obj,'coords','dimension'),'height'))
    s += ' ' + str(get(obj,'coords','gop'))
    if hasattr(get(obj,'coords'), 'margin'):
      s += ' ' + str(get(get(obj,'coords','margin'),'x'))
      s += ' ' + str(get(get(obj,'coords','margin'),'y'))
    out.append(s + ";\r\n")

def getCanvas(obj, out, root=False):
  """ Parses the canvas entry into pd-lingo 
  
  Description
  -----------  
    This function takes a python object `obj` (coming from json),
    and an `out` list. 
    It also takes a boolean `root` to indicate if it is the root object.
    If it is not the root, it will recurse through the nodes.
  
  It returns `None`, but they append pd-formatted strings to the `out` list
  
  """
  # Get the depth and add a new element with -1
  global depth
  depth.append(-1)
  
  s = '#N canvas'
  s += ' ' + str(get(obj,'screen','x'))
  s += ' ' + str(get(obj,'screen','y'))
  s += ' ' + str(get(obj,'dimension','width'))
  s += ' ' + str(get(obj,'dimension','height'))
  # Do not add name and vis flag if it is the root, add font instead
  if root:
    s += ' ' + str(get(obj,'font'))    
  else:
    s += ' ' + get(obj,'name')
    s += f" {'1' if get(obj,'vis') else '0'}"
  
  out.append(s + ";\r\n")
  
  # recurse through the nodes if it is not the root
  if not root:
    getNodes(obj, out)
    getComments(obj, out)
    getConnections(obj, out)
    getCoords(obj, out)
    getRestore(obj, out)
    getBorder(obj, out)

def getNativeGui(x, kind):
  """ Parses the gui entry into pd-lingo 
  
  Description
  -----------  
    This function formats the string into the native gui string format
  
  Return
  ----------
    A native gui pd-string
  
  """
  s = f"#X {kind}"
  s += ' ' + str(int(get(x,'position','x')))
  s += ' ' + str(int(get(x,'position','y')))

  if hasattr(x, "digit_width"):
    s += ' ' + str(int(get(x,'digit_width')))
  else:
    s += ' 0'

  if hasattr(x, "limits"):
    s += ' ' + str(int(get(x,'limits','lower')))
    s += ' ' + str(int(get(x,'limits','upper')))
  else:
    s += ' 0 0'

  if hasattr(x, "flag"):
    s += ' ' + str(int(get(x,'flag')))
  else:
    s += ' 0'
  
  if hasattr(x, "label"):
    s += ' ' + get(x,'label')
  else:
    s += ' -'

  if hasattr(x, "receive"):
    s += ' ' + get(x,'receive')
  else:
    s += ' -'

  if hasattr(x, "send"):
    s += ' ' + get(x,'send')
  else:
    s += ' -'
  
  return s
  