#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Json-formatted file (Python Patch Object) to Pure data file """

from ..util.utils import log
from ..classes.default import GOPArrayFlags, PdNativeGuiNames, IEMGuiNames, Default

__all__ = [ "JsonToPd" ]

class JsonToPd:

  def __init__(self, obj):
    
    if not hasattr(obj, 'root'):
      raise Exception("JsonToPd: No root object")
    
    self.obj = obj
    self.root = getattr(obj, 'root')
    self.name = self.obj.patchname  
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
      self.getCanvas(self.obj.root, root=True)
      # add declarations
      self.getDependencies()
      # add nodes
      self.getNodes(self.obj.root)
      # add comments
      self.getComments(self.obj.root)
      # add coords
      self.getCoords(self.obj.root)
      # add connections
      self.getConnections(self.obj.root)
      # add restore (if gop)
      self.getRestore(self.obj.root)
    
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
      s += ' ' + str(getattr(screen,'x'))
      s += ' ' + str(getattr(screen,'y'))
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
        if hasattr(x, 'position'):
          pos = getattr(x, 'position')
          s += f" {str(getattr(pos,'x'))} {str(getattr(pos,'y'))} "
        else:
          log(1,"Comment has no position.")
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
            if hasattr(x, 'position'):
              pos = getattr(x, 'position')
              s += ' ' + str(getattr(pos,'x'))
              s += ' ' + str(getattr(pos,'y'))
          else:
            log(1,"WARNING, UNPARSED", x)
        else:
          className = getattr(x, 'className')
          
          if 'msg' == className:
            s += '#X msg'
            if hasattr(x, 'position'):
              pos = getattr(x, 'position')
              s += ' ' + str(getattr(pos,'x'))
              s += ' ' + str(getattr(pos,'y'))
            if hasattr(x, "targets"):
              for t in getattr(x,'targets'):
                if 'outlet' == getattr(t,'address'):
                  msg = getattr(t,'message')
                  s += ' ' + ' \\, '.join(msg)
                else:
                  s += ' \\; ' + getattr(t,'address') + ' ' + ' \\, '.join(getattr(t,'message'))
          
          elif "scalar" == className:
            s += "#X scalar"
            s += ' ' + getattr(x,'name')
            #TODO: fix scalar to new struct schema
            for e in getattr(x,'data'):
              log(1,"SCALAR", e)
              if hasattr(obj,'struct'):
                log(1,"STRUCT", obj.struct)
              s += ' ' + ' '.join(e) + " \;"
          
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
            if hasattr(x, 'position'):
              pos = getattr(x, 'position')
              s += ' ' + str(getattr(pos,'x'))
              s += ' ' + str(getattr(pos,'y'))
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

              def addarea(s, name):
                if hasattr(x, 'area'):
                  a = getattr(x, 'area')
                  s += ' ' + str(getattr(a,'width' ,self.__d__.iemgui[name]['width']))
                  s += ' ' + str(getattr(a,'height',self.__d__.iemgui[name]['height']))
                else:
                  s += ' ' + str(self.__d__.iemgui[name]['width'])
                  s += ' ' + str(self.__d__.iemgui[name]['height'])

              def addfont(s, name):
                if hasattr(x, 'font'):
                  f = getattr(x, 'font')
                  s+= ' ' + str(getattr(f,'face',self.__d__.iemgui['fontface']))
                  s+= ' ' + str(getattr(f,'size',self.__d__.iemgui[name]['fsize']))
                else:
                  s += ' ' + str(self.__d__.iemgui['fontface'])
                  s += ' ' + str(self.__d__.iemgui[name]['fsize'])

              def addlimits(s, name):
                if hasattr(x, 'limits'):
                  f = getattr(x, 'limits')
                  s+= ' ' + str(getattr(f,'upper',self.__d__.iemgui[name]['upper']))
                  s+= ' ' + str(getattr(f,'lower',self.__d__.iemgui[name]['lower']))
                else:
                  s += ' ' + str(self.__d__.iemgui[name]['upper'])
                  s += ' ' + str(self.__d__.iemgui[name]['lower'])
              
              def addprop(s, name, prop, bool=False, _global=False):
                if not _global:
                  _default = self.__d__.iemgui[name][prop]
                else:
                  _default = self.__d__.iemgui[prop]
                
                if not bool:
                  s += ' ' + str(getattr(x, prop, _default))
                else:
                  s += ' 1' if getattr(x, prop, _default) else ' 0'
              

              if "vu" == className:
                addarea(s, 'vu')
                s += f" {receive} {label}"
                addoffset(s, 'vu')
                addfont(s, 'vu')
                addprop(s, 'vu', 'bgcolor')
                addprop(s, 'vu', 'lbcolor')
                addprop(s, 'vu', 'scale', bool=True)
                addprop(s, 'vu', 'flag', bool=True)
              
                
              elif "cnv" == className or "my_canvas" == className:
                addprop(s, 'cnv', 'size')
                addarea(s, 'cnv')
                s+=f" {send} {receive} {label}" if send is not None else f" {receive} {label}"
                addoffset(s, 'cnv')
                addfont(s, 'cnv')
                addprop(s, 'cnv', 'bgcolor')
                addprop(s, 'cnv', 'lbcolor')
                addprop(s, 'cnv', 'flag', bool=True)

              elif "tgl" == className:
                addprop(s, 'tgl', 'size')
                addprop(s, 'tgl', 'init', bool=True)
                s += f" {send} {receive} {label}"
                addoffset(s, 'tgl')
                addfont(s, 'tgl')
                addprop(s, 'tgl', 'bgcolor')
                addprop(s, 'tgl', 'fgcolor', _global=True)
                addprop(s, 'tgl', 'lbcolor')
                addprop(s, 'tgl', 'flag', bool=True)
                addprop(s, 'tgl', 'nonzero')
              
              elif "radio" in className or 'rdb' == className:
                addprop(s, 'radio', 'size')
                addprop(s, 'radio', 'flag', bool=True)
                addprop(s, 'radio', 'init', bool=True)
                addprop(s, 'radio', 'number')
                s += f" {send} {receive} {label}"
                addoffset(s, 'radio')
                addfont(s, 'radio')
                addprop(s, 'radio', 'bgcolor')
                addprop(s, 'radio', 'fgcolor', _global=True)
                addprop(s, 'radio', 'lbcolor')
                addprop(s, 'radio', 'value')


              elif 'bng' == className:
                addprop(s, 'bng', 'size')
                addprop(s, 'bng', 'hold')
                addprop(s, 'bng', 'intrrpt')
                addprop(s, 'bng', 'init', bool=True)
                s += f" {send} {receive} {label}"
                addoffset(s, 'bng')
                addfont(s, 'bng')
                addprop(s, 'bng', 'bgcolor')
                addprop(s, 'bng', 'fgcolor', _global=True)
                addprop(s, 'bng', 'lbcolor')

              elif 'nbx' == className:
                addprop(s, 'nbx', 'digits_width')
                addprop(s, 'nbx', 'height')
                addlimits(s, 'nbx')
                addprop(s, 'nbx', 'log_flag')
                addprop(s, 'nbx', 'init', bool=True)
                s += f" {send} {receive} {label}"
                addoffset(s, 'nbx')
                addfont(s, 'nbx')
                addprop(s, 'nbx', 'bgcolor')
                addprop(s, 'nbx', 'fgcolor', _global=True)
                addprop(s, 'nbx', 'lbcolor')
                addprop(s, 'nbx', 'value')
                addprop(s, 'nbx', 'log_height')

              elif 'hsl' == className:
                addarea(s, 'hsl')
                addlimits(s, 'hsl')
                addprop(s, 'hsl', 'log_flag')
                addprop(s, 'hsl', 'init', bool=True)
                s += f" {send} {receive} {label}"
                addoffset(s, 'hsl')
                addfont(s, 'hsl')
                addprop(s, 'hsl', 'bgcolor')
                addprop(s, 'hsl', 'fgcolor', _global=True)
                addprop(s, 'hsl', 'lbcolor')
                addprop(s, 'hsl', 'value')
                addprop(s, 'hsl', 'steady', bool=True)
              
              elif 'vsl' == className:
                addarea(s, 'vsl')
                addlimits(s, 'vsl')
                addprop(s, 'vsl', 'log_flag')
                addprop(s, 'vsl', 'init', bool=True)
                s += f" {send} {receive} {label}"
                addoffset(s, 'vsl')
                addfont(s, 'vsl')
                addprop(s, 'vsl', 'bgcolor')
                addprop(s, 'vsl', 'fgcolor', _global=True)
                addprop(s, 'vsl', 'lbcolor')
                addprop(s, 'vsl', 'value')
                addprop(s, 'vsl', 'steady', bool=True)
              
              else:
                log(2,"Can't parse PdIEMGui", x)

            
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
    
    if hasattr(obj, 'position'):
      s = '#X restore'
      pos = getattr(obj,'position')
      s += ' ' + str(getattr(pos,'x'))
      s += ' ' + str(getattr(pos,'y'))
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
      pos = getattr(coords,'position')
      a = getattr(range,'a')
      b = getattr(range,'b')

      s = '#X coords'
      s += ' ' + str(getattr(a,'x'))
      s += ' ' + str(getattr(b,'x'))
      s += ' ' + str(getattr(a,'y'))
      s += ' ' + str(getattr(b,'y'))
      s += ' ' + str(getattr(pos,'width'))
      s += ' ' + str(getattr(pos,'height'))
      s += ' ' + str(getattr(coords,'gop'))
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
    pos = getattr(x,'position')
    s += ' ' + str(int(getattr(pos,'x')))
    s += ' ' + str(int(getattr(pos,'y')))
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
    