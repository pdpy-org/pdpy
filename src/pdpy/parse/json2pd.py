#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Json-formatted file (Python Patch Object) to Pure data file """

from ..util.utils import log
from ..classes.default import GOPArrayFlags, PdNativeGuiNames, IEMGuiNames, Default
from ..classes.data_structures import Scalar

__all__ = [ "JsonToPd" ]

class JsonToPd:

  def __init__(self, obj):
    
    # log(1, "JsonToPd: Parsing", obj)
    if not hasattr(obj,'root'):
      raise Exception("JsonToPd: No root object")
    
    self.obj = obj
    self.root = getattr(self.obj,'root')
    self.name = getattr(self.obj,'patchname')
    self.pd = []
    self.__d__ = Default()

    # This is a list that holds the self.depth of the current object
    self.depth = []

    # This is a dictionary with 
    # - the node indices as keys, and 
    # - the last self.depth index as values
    self.obj_map = {}

    # The pd line end character sequence
    self.end = ';\r\n'

    self.parse()

  def parse(self):
      # print(o.toJSON())
      # add structs
      self.getStruct()
      # add main root canvas
      self.getCanvas(getattr(self.obj,'root'), root=True)
      # add declarations
      self.getDependencies()
      # add nodes
      self.getNodes(getattr(self.obj,'root'))
      # add comments
      self.getComments(getattr(self.obj,'root'))
      # add coords
      self.getCoords(getattr(self.obj,'root'))
      # add connections
      self.getConnections(getattr(self.obj,'root'))
      # add restore (if gop)
      self.getRestore(getattr(self.obj,'root'))
    
  def getpd(self):
    """ Returns the pd array as a string """
    return "".join(self.pd)

  # ************************************************************************** #
  # Routines to keep track of object connections
  # ************************************************************************** #

  def map_idx(self, id):
    """ Maps a node id to a unique index """
    # get the self.depth and self.obj_map globals
    
    
    # increment the last self.depth index by one
    self.depth[-1] += 1
    # add the node to the map
    self.obj_map.update({ id : self.depth[-1] })

  def remap(self, id):
    """ Get the value from the mapped indices """
    # get the object map
    
    s = '-1'
    try:
      # query the map for the value at the id key
      s = str( self.obj_map[int(id)] )
    except KeyError:
      # if the key is not found, log the error
      log(1, "remap()::Key Not Found", id)
      print(self.obj_map)
    finally:
      # return the value
      return s

  # ************************************************************************** #
  # TODO: Define a custom decoder
  # ************************************************************************** #

  # def PdPyDecoder(obj):
  #   if "__type__" in obj and obj["__type__"] == "PdPy":
  #     o = PdPy(obj["patchname"], obj["encoding"])
  #   else:
  #     return lambda d: SimpleNamespace(**d)

  # ************************************************************************** #
  # Helper to get the property of an object
  # ************************************************************************** #

  def get(self, obj, prop, subprop=None, default=None):

    if isinstance(obj, dict) or isinstance(obj, list):
      o = obj[prop]
    else:
      o = getattr(obj, str(prop))
    
    if subprop is None:
      return o if o is not None else default
    else:
      return self.get(o, subprop)

  # ************************************************************************** #
  # Routines to get data from structured pdpy json file into pd-formatted string
  # ************************************************************************** #

  def getStruct(self):
    """ Parses the struct entry into pd-lingo 
    
    Description
    -----------  
      This function takes a python object `obj` (coming from json),
      and an `out` list. 
    
    It returns `None`, but they append pd-formatted strings to the `out` list
    
    """
    if hasattr(self.obj, 'struct'):
      for d in getattr(self.obj,'struct'):
        s = f"#N struct {getattr(d,'name')}"

        if hasattr(d, 'float'):
          s += ' '
          s += ' '.join([ f"float {x}" for x in getattr(d,'float') ])
        
        if hasattr(d, 'symbol'):
          s += ' '
          s += ' '.join([ f"symbol {x}" for x in getattr(d,'symbol') ])
        
        if hasattr(d, 'text'):
          s += ' '
          s += ' '.join([ f"text {x}" for x in getattr(d,'text') ])
        
        if hasattr(d, 'array'):
          s += ' '
          s += ' '.join([ f"array {getattr(x,'name')} {getattr(x,'template')}" for x in getattr(d,'array') ])
        
        self.pd.append(s + self.end)
  # end of getStruct ----------------------------------------------------------

  def getCanvas(self, obj, root=False):
    """ Parses the canvas entry into pd-lingo 
    
    Description
    -----------  
      This function takes a python object `obj` (coming from json),
      and an `out` list. 
      It also takes a boolean `root` to indicate if it is the root object.
      If it is not the root, it will recurse through the nodes.
    
    It returns `None`, but they append pd-formatted strings to the `out` list
    
    """
    # Get the self.depth and add a new element with -1
    
    self.depth.append(-1)
    
    s = '#N canvas'
    if hasattr(obj, 'screen'):
      screen = getattr(obj, 'screen')
      s += screen.__pd__()
    if hasattr(obj, 'dimension'):
      dimension = getattr(obj, 'dimension')
      s += ' ' + str(getattr(dimension,'width'))
      s += ' ' + str(getattr(dimension,'height'))
    # Do not add name and vis flag if it is the root, add font instead
    if root and hasattr(obj, 'font'):
      s += ' ' + str(getattr(obj,'font'))    
    else:
      s += ' ' + getattr(obj,'name')
      s += f" {'1' if getattr(obj,'vis') else '0'}"
    
    self.pd.append(s + self.end)
    
    # recurse through the nodes if it is not the root
    if not root:
      self.getNodes(obj)
      self.getComments(obj)
      self.getConnections(obj)
      self.getCoords(obj)
      self.getRestore(obj)
      self.getBorder(obj)

  def getDependencies(self):
    """ Parses the dependencies entry into paths and libs """
    if hasattr(self.obj, "dependencies"):
      dependencies = getattr(self.obj, "dependencies")
      if hasattr(dependencies, 'paths'):
        s = "#X declare"
        for x in getattr(dependencies, 'paths'):
          s += f" -path {x}"
        self.pd.append(s + self.end)
      if hasattr(dependencies, 'libs'):
        s = "#X declare"
        for x in getattr(dependencies, 'libs'):
          s += f" -lib {x}"
        self.pd.append(s + self.end)

  def getComments(self, obj):
    """ Parses the comment entry into pd-lingo 
    
    Description
    -----------  
      This function takes a python object `obj` (coming from json),
      and an `out` list. 
    
    It returns `None`, but they append pd-formatted strings to the `out` list
    
    """

    if hasattr(obj, 'comments'):
      for x in getattr(obj,'comments'):
        s = "#X text"
        s = self.addpos(s, x)
        if hasattr(x, 'text'):
          text = getattr(x, 'text')
          if len(text) == 1: 
            s += text[0]
          else: 
            s += ' '.join([ f"{t} \\;" for t in text ])
        else:
          log(1, "Comment has no text.")
        # TODO: is this placing doubly escaped commas?
        s = s.replace(',',' \\,')
        if hasattr(x, 'border'): 
          s += f", f {str(getattr(x,'border'))}"
        self.pd.append(s + self.end)

  def getConnections(self, obj):
    """ Parses the connections entry into pd-lingo 
    
    Description
    -----------  
      This function takes a python object `obj` (coming from json),
      and an `out` list. 
    
    It returns `None`, but they append pd-formatted strings to the `out` list
    
    """
    if hasattr(obj, 'edges'):
      for x in getattr(obj,'edges'):
        s = "#X connect"
        src = getattr(x, 'source')
        snk = getattr(x, 'sink')
        s += f" {self.remap(getattr(src,'id'))} {str(getattr(src,'port'))}"
        s += f" {self.remap(getattr(snk,'id'))} {str(getattr(snk,'port'))}"
        if '-1' not in s:
          self.pd.append(s + self.end)
        else:
          log(1,"EDGES", x)
          log(1,"Missed a connection:", s)

  def addpos(self, pd_string, json_object):
    if hasattr(json_object, 'position'):
      pd_string += getattr(json_object, 'position').__pd__()
    return pd_string

  def getNodes(self, obj):
    """ Parses the nodes entry into pd-lingo 
    
    Description
    -----------  
      This function takes a python object `obj` (coming from json),
      and an `out` list. 
    
    It returns `None`, but they append pd-formatted strings to the `out` list
    
    """
    
    if hasattr(obj, 'nodes'):
      haso = False
      for x in getattr(obj, 'nodes'):
        s = ''
        
        # If the node has an ID, get it and use it to update the object map
        if hasattr(x,"id"):
          # update the object map
          self.map_idx(int(getattr(x,'id')))
          # uncomment to see the mapping on the pd-file
          # s += ' ' + str(self.obj_map[get(x,'id')]) + ' '
  
        if hasattr(x, 'nodes'):
          # uncomment to see the mapping on the pd-file
          # out.append(str(self.obj_map[get(x,'id')]) + ' ')
          self.getCanvas(x)
        elif not hasattr(x, 'className'):
          # TODO: avoid these checks 
          if getattr(x, "__pdpy__") == "PdObject":
            s += "#X obj"
            s = self.addpos(s, x)
          else:
            log(1,"WARNING, UNPARSED", x)
        else:
          className = getattr(x, 'className')
          
          if 'msg' == className:
            s += '#X msg'
            s = self.addpos(s, x)
            
            if hasattr(x, "targets"):
              for t in getattr(x,'targets'):
                if 'outlet' == getattr(t,'address'):
                  msg = getattr(t,'message')
                  s += ' ' + ' \\, '.join(msg)
                else:
                  s += ' \\; ' + getattr(t,'address') + ' ' + ' \\, '.join(getattr(t,'message'))
          
          elif "scalar" == className:
            scalar = Scalar(struct=self.obj.struct, json_dict=x)
            # scalar.dumps()
            s = scalar.getPd()
            
          elif className in PdNativeGuiNames:
            s += self.getNativeGui(x, className)
          
          elif "goparray" == className:
            s += "#X array"
            s += ' ' + getattr(x,'name')
            s += ' ' + str(getattr(x,'size'))
            s += ' float'
            s += ' ' + str(GOPArrayFlags.index(getattr(x,'flag')))
          
          else:

            # TODO
            # IEMGUI stuff
            # more granular control on each param

            s += "#X obj"
            s = self.addpos(s, x)
            s += ' ' + className
            
            if className in IEMGuiNames:
              # log(1,x)
              # s += ' ' + ' '.join(get(x,'args'))
              
              receive = getattr(x,'receive', self.__d__.iemgui['symbol'])
              send    = getattr(x,'send', self.__d__.iemgui['symbol'])
              label   = getattr(x,'label', self.__d__.iemgui['symbol'])
              

              def addoffset(s, name):
                if hasattr(x, 'offset'):
                  o = getattr(x, 'offset')
                  s += ' ' + str(getattr(o,'x',self.__d__.iemgui[name]['xoff']))
                  s += ' ' + str(getattr(o,'y',self.__d__.iemgui[name]['yoff']))
                else:
                  s += ' ' + str(self.__d__.iemgui[name]['xoff'])
                  s += ' ' + str(self.__d__.iemgui[name]['yoff'])
                return s

              def addarea(s, name):
                if hasattr(x, 'area'):
                  a = getattr(x, 'area')
                  s += ' ' + str(getattr(a,'width' ,self.__d__.iemgui[name]['width']))
                  s += ' ' + str(getattr(a,'height',self.__d__.iemgui[name]['height']))
                else:
                  s += ' ' + str(self.__d__.iemgui[name]['width'])
                  s += ' ' + str(self.__d__.iemgui[name]['height'])
                return s

              def addfont(s, name):
                if hasattr(x, 'font'):
                  f = getattr(x, 'font')
                  s+= ' ' + str(getattr(f,'face',self.__d__.iemgui['fontface']))
                  s+= ' ' + str(getattr(f,'size',self.__d__.iemgui[name]['fsize']))
                else:
                  s += ' ' + str(self.__d__.iemgui['fontface'])
                  s += ' ' + str(self.__d__.iemgui[name]['fsize'])
                return s

              def addlimits(s, name):
                if hasattr(x, 'limits'):
                  f = getattr(x, 'limits')
                  s+= ' ' + str(getattr(f,'upper',self.__d__.iemgui[name]['upper']))
                  s+= ' ' + str(getattr(f,'lower',self.__d__.iemgui[name]['lower']))
                else:
                  s += ' ' + str(self.__d__.iemgui[name]['upper'])
                  s += ' ' + str(self.__d__.iemgui[name]['lower'])
                return s
              
              def addprop(s, name, prop, bool=False, _global=False):
                if not _global:
                  _default = self.__d__.iemgui[name][prop]
                else:
                  _default = self.__d__.iemgui[prop]
                
                if not bool:
                  s += ' ' + str(getattr(x, prop, _default))
                else:
                  s += ' 1' if getattr(x, prop, _default) else ' 0'
                return s

              if "vu" == className:
                s = addarea(s, 'vu')
                s += f" {receive} {label}"
                s = addoffset(s, 'vu')
                s = addfont(s, 'vu')
                s = addprop(s, 'vu', 'bgcolor')
                s = addprop(s, 'vu', 'lbcolor')
                s = addprop(s, 'vu', 'scale', bool=True)
                s = addprop(s, 'vu', 'flag', bool=True)
              
                
              elif "cnv" == className or "my_canvas" == className:
                s = addprop(s, 'cnv', 'size')
                s = addarea(s, 'cnv')
                s+=f" {send} {receive} {label}" if send is not None else f" {receive} {label}"
                s = addoffset(s, 'cnv')
                s = addfont(s, 'cnv')
                s = addprop(s, 'cnv', 'bgcolor')
                s = addprop(s, 'cnv', 'lbcolor')
                s = addprop(s, 'cnv', 'flag', bool=True)

              elif "tgl" == className:
                s = addprop(s, 'tgl', 'size')
                s = addprop(s, 'tgl', 'init', bool=True)
                s += f" {send} {receive} {label}"
                s = addoffset(s, 'tgl')
                s = addfont(s, 'tgl')
                s = addprop(s, 'tgl', 'bgcolor')
                s = addprop(s, 'tgl', 'fgcolor', _global=True)
                s = addprop(s, 'tgl', 'lbcolor')
                s = addprop(s, 'tgl', 'flag', bool=True)
                s = addprop(s, 'tgl', 'nonzero')
              
              elif "radio" in className or 'rdb' == className:
                s = addprop(s, 'radio', 'size')
                s = addprop(s, 'radio', 'flag', bool=True)
                s = addprop(s, 'radio', 'init', bool=True)
                s = addprop(s, 'radio', 'number')
                s += f" {send} {receive} {label}"
                s = addoffset(s, 'radio')
                s = addfont(s, 'radio')
                s = addprop(s, 'radio', 'bgcolor')
                s = addprop(s, 'radio', 'fgcolor', _global=True)
                s = addprop(s, 'radio', 'lbcolor')
                s = addprop(s, 'radio', 'value')


              elif 'bng' == className:
                s = addprop(s, 'bng', 'size')
                s = addprop(s, 'bng', 'hold')
                s = addprop(s, 'bng', 'intrrpt')
                s = addprop(s, 'bng', 'init', bool=True)
                s += f" {send} {receive} {label}"
                s = addoffset(s, 'bng')
                s = addfont(s, 'bng')
                s = addprop(s, 'bng', 'bgcolor')
                s = addprop(s, 'bng', 'fgcolor', _global=True)
                s = addprop(s, 'bng', 'lbcolor')

              elif 'nbx' == className:
                s = addprop(s, 'nbx', 'digits_width')
                s = addprop(s, 'nbx', 'height')
                s = addlimits(s, 'nbx')
                s = addprop(s, 'nbx', 'log_flag')
                s = addprop(s, 'nbx', 'init', bool=True)
                s += f" {send} {receive} {label}"
                s = addoffset(s, 'nbx')
                s = addfont(s, 'nbx')
                s = addprop(s, 'nbx', 'bgcolor')
                s = addprop(s, 'nbx', 'fgcolor', _global=True)
                s = addprop(s, 'nbx', 'lbcolor')
                s = addprop(s, 'nbx', 'value')
                s = addprop(s, 'nbx', 'log_height')

              elif 'hsl' == className:
                s = addarea(s, 'hsl')
                s = addlimits(s, 'hsl')
                s = addprop(s, 'hsl', 'log_flag')
                s = addprop(s, 'hsl', 'init', bool=True)
                s += f" {send} {receive} {label}"
                s = addoffset(s, 'hsl')
                s = addfont(s, 'hsl')
                s = addprop(s, 'hsl', 'bgcolor')
                s = addprop(s, 'hsl', 'fgcolor', _global=True)
                s = addprop(s, 'hsl', 'lbcolor')
                s = addprop(s, 'hsl', 'value')
                s = addprop(s, 'hsl', 'steady', bool=True)
              
              elif 'vsl' == className:
                s = addarea(s, 'vsl')
                s = addlimits(s, 'vsl')
                s = addprop(s, 'vsl', 'log_flag')
                s = addprop(s, 'vsl', 'init', bool=True)
                s += f" {send} {receive} {label}"
                s = addoffset(s, 'vsl')
                s = addfont(s, 'vsl')
                s = addprop(s, 'vsl', 'bgcolor')
                s = addprop(s, 'vsl', 'fgcolor', _global=True)
                s = addprop(s, 'vsl', 'lbcolor')
                s = addprop(s, 'vsl', 'value')
                s = addprop(s, 'vsl', 'steady', bool=True)
              
              else:
                log(2,"Can't parse PdIEMGui", x)
              # log(1,"IEMGui", s)

            
            else:
              
              if hasattr(x, "subclass"):
                s += ' ' + getattr(x,'subclass')
              
              if hasattr(x, "keep") and getattr(x,'keep'):
                s += ' -k'

              if hasattr(x, "name"):
                s += ' ' + getattr(x,'name')
              
              if hasattr(x, "size"):
                s += ' ' + str(getattr(x,'size'))

              if hasattr(x, "data"):
                # flag to append data on next line
                haso = True
                
              if hasattr(x,"args"):
                args = getattr(x,'args')
                # print("ARGUMENTS",args,type(args))
                if isinstance(args, list):
                  s += ' ' + ' '.join(args)
                else:
                  s += args
          
          self.pd.append(s + self.end)
          self.getBorder(x)  

        if haso:
          s = "#A" + ' set' if "text" == className else ' saved'
          for e in getattr(x,'data'):
            if isinstance(e, str):
              s += ' ' + e
            elif isinstance(e, list):
              s += ' ' + ' '.join(e) + " \\;"
            else:
              s += ' ' + str(e)
          
          self.pd.append(s + self.end)
          haso = False

  def getRestore(self, obj):
    """ Parses the restore entry into pd-lingo 
    
    Description
    -----------  
      This function takes a python object `obj` (coming from json),
      and an `out` list. 
    
    It returns `None`, but they append pd-formatted strings to the `out` list
    
    """
    # Get the self.depth and remove the last element
    
    self.depth.pop()
    
    if hasattr(obj, 'title'):
      s = '#X restore'
      s = self.addpos(s, obj)
      s += ' ' + getattr(obj,'title')
      self.pd.append(s + self.end)

  def getBorder(self, obj):
    """ Parses the border entry into pd-lingo 
    
    Description
    -----------  
      This function takes a python object `obj` (coming from json),
      and an `out` list. 
    
    It returns `None`, but they append pd-formatted strings to the `out` list
    
    """
    if hasattr(obj, 'border'):
      s = '#X f ' + str(getattr(obj,'border'))
      self.pd.append(s + self.end)

  def getCoords(self, obj):
    """ Parses the coords entry into pd-lingo 
    
    Description
    -----------  
      This function takes a python object `obj` (coming from json),
      and an `out` list. 
    
    It returns `None`, but they append pd-formatted strings to the `out` list
    
    """
    if hasattr(obj, 'coords'):
      coords = getattr(obj,'coords')
      range = getattr(coords,'range')
      dimension = getattr(coords,'dimension')
      a = getattr(range,'a')
      b = getattr(range,'b')

      s = '#X coords'
      s += f" {getattr(a,'x')} {getattr(b,'x')}"
      s += f" {getattr(a,'y')} {getattr(b,'y')}"
      s += f" {getattr(dimension,'width')} {getattr(dimension,'height')}"
      s += f" {getattr(coords,'gop')}"
      if hasattr(coords, 'margin'):
        margin = getattr(coords,'margin')
        s += ' ' + str(getattr(margin,'x'))
        s += ' ' + str(getattr(margin,'y'))
      self.pd.append(s + self.end)

  def getNativeGui(self, x, className):
    """ Parses the gui entry into pd-lingo 
    
    Description
    -----------  
      This function formats the string into the native gui string format
    
    Return
    ----------
      A native gui pd-string
    
    """
    s = '#X ' + className
    s = self.addpos(s, x)
    s += ' ' + str(int(getattr(x,'digit_width',self.__d__.digits_width)))
    
    if hasattr(x, "limits"):
      limits = getattr(x,'limits')
      s += ' ' + str(int(getattr(limits,'lower',self.__d__.limits['lower'])))
      s += ' ' + str(int(getattr(limits,'upper',self.__d__.limits['upper'])))
    else:
      s += f" {self.__d__.limits['lower']} {self.__d__.limits['upper']}"

    s += ' ' + str(int(getattr(x,'flag', self.__d__.flag)))
    s += ' ' + getattr(x,'label',self.__d__.label)
    s += ' ' + getattr(x,'receive',self.__d__.receive)
    s += ' ' + getattr(x,'send',self.__d__.send)

    return s
    