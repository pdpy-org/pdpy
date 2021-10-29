#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Json-formatted file (Python Patch Object) to XML file """

from ..util.utils import log
from ..classes.classes import GOPArrayFlags

import xml.etree.ElementTree as ET

__all__ = [ "JsonToXml" ]

class JsonToXml:
  
  def __init__(self, obj):

    # do not continue loading if root is not present
    if not hasattr(obj, "root"):
      return

    # The json as python object
    self.obj = obj

    # This is a list that holds the self.depth of the current object
    self.depth = []

    # This is a dictionary with 
    # - the node indices as keys, and 
    # - the last self.depth index as values
    self.obj_map = {}

    self.et = ET.ElementTree('patch', attributes={'name':self.obj.patchname})

    # add structs
    self.getStruct()
    # add main root canvas
    self.getCanvas(self.obj, root=True)
    # add declarations
    self.getDependencies()
    # add nodes
    self.getNodes()
    # add comments
    self.getComments()
    # add coords
    self.getCoords()
    # add connections
    self.getConnections()
    # add restore (if gop)
    self.getRestore()


  def __map_idx__(self, id):
    """ Maps a node id to a unique index """
    # increment the last self.depth index by one
    self.depth[-1] += 1
    # add the node to the map
    self.obj_map.update({ id : self.depth[-1] })

  def __remap__(self, id):
    """ Get the value from the mapped indices """
    # get the object map
    
    s = '-1'
    try:
      # query the map for the value at the id key
      s = str( self.obj_map[int(id)] )
    except KeyError:
      # if the key is not found, log the error
      log(1, "__remap__()::Key Not Found", id)
      print(self.obj_map)
    finally:
      # return the value
      return s


  def get(self, prop, subprop=None, default=None):

    if isinstance(self.obj, dict) or isinstance(self.obj, list):
      o = self.obj[prop]
    else:
      o = getattr(self.obj, str(prop))
    
    if subprop is None:
      return o if o is not None else default
    else:
      return self.get(o, subprop)

  # **************************************************************************** #
  # Routines to get data from structured pdpy json file into pd-formatted string
  # **************************************************************************** #

  def getStruct(self):
    """ Parses the struct entry into pd-lingo 
    
    Description
    -----------  
      This function takes a python object `obj` (coming from json),
      and an `out` list. 
    
    It returns `None`, but they append pd-formatted strings to the `out` list
    
    """
    if hasattr(self.obj, 'struct'):
      for d in self.get(self,'struct'):
        struct = ET.SubElement(self.et, 'struct')
        ET.SubElement(struct, 'name').text = self.get(d,'name')

        if hasattr(d, 'float'):
          ET.SubElement(struct, 'float').text = self.get(d,'float')
        
        if hasattr(d, 'symbol'):
          ET.SubElement(struct, 'symbol').text = self.get(d,'symbol')
        
        if hasattr(d, 'text'):
          ET.SubElement(struct, 'text').text = self.get(d,'text')
        
        if hasattr(d, 'array'):
          for x in self.get(d,'array'):
            array = ET.SubElement(struct, 'array')
            ET.SubElement(array, 'name').text = self.get(x,'name')
            ET.SubElement(array, 'template').text = self.get(x,'template')
        
        

  def getComments(self):
    if hasattr(self.obj, 'comments'):
      for x in self.get(self.obj,'comments'):
        comment = ET.SubElement(self.et, 'comment')
 
        ET.SubElement(comment, 'xpos').text = self.get(x,'position','x')
        ET.SubElement(comment, 'ypos').text = self.get(x,'position','y')

        if len(self.get(x,'text')) == 1: 
          comment.text = self.get(x, 'text', 0)
        else: 
          comment.text = ' '.join([ f"{t} \\;" for t in self.get(x,'text') ])
        
        if hasattr(x, 'border'): 
          ET.SubElement(comment, 'xpos').text = self.get(x,'border')
        

  def getConnections(self):
    if hasattr(self.obj, 'edges'):
      for x in self.get(self.obj,'edges'):
        connect = ET.SubElement(self.et, 'connect')
        source = ET.SubElement(connect, 'source')
        sink = ET.SubElement(connect, 'sink')

        ET.SubElement(source, 'id').text = self.__remap__(self.get(x,'source','id'))
        ET.SubElement(source, 'port').text = self.get(x,'source','port')
        ET.SubElement(sink, 'id').text = self.__remap__(self.get(x,'sink','id'))
        ET.SubElement(sink, 'port').text = self.get(x,'sink','port')

  def getNodes(self):
    # uncomment this to add a comment offset
    # c_offset =  len(get(obj,'comments'))-1 if hasattr(obj, 'comments') else 0
    c_offset = 0
    
    if hasattr(self.obj, 'nodes'):
      haso = False
      for x in self.obj.nodes:
        # If the node has an ID, get it and use it to update the object map
        if hasattr(x,"id"):
          # update the object map
          self.__map_idx__(int(self.get(x,'id'))-c_offset)
          
        if self.get(x, "__pdpy__") == "Canvas":
          # a canvas, recurse
          self.getCanvas(x)
        elif not hasattr(x, 'className'):
          # an empty object
          if self.get(x, "__pdpy__") == "PdObject":
            e = ET.SubElement(self.et, 'obj')
            ET.SubElement(e, 'xpos').text = self.get(x,'position','x')
            ET.SubElement(e, 'ypos').text = self.get(x,'position','y')
          else:
            log(1,"WARNING, UNPARSED", x)
        else:
          # anything else will be created
          

          if self.get(x, "__pdpy__") == "PdMessage":
            
            """ A Pd Message """
            
            e = ET.SubElement(self.et, 'msg')
            ET.SubElement(e, 'xpos').text = self.get(x,'position','x')
            ET.SubElement(e, 'ypos').text = self.get(x,'position','y')
            if hasattr(x, "targets"):
              for t in self.get(x,'targets'):
                ET.SubElement(e, 'target').text = self.get(t,'address')
                for m in self.get(t,'message'):
                  ET.SubElement(e, 'message').text = m



          elif self.get(x, "__pdpy__") == "Scalar":
            
            """ A Pd Scalar """
          
            s += "#X scalar"
            s += ' ' + self.get(x,'name')
          
            for e in self.get(x,'data'):
              s += ' ' + ' '.join(e) + " \;"
          
          elif self.get(x, "__pdpy__") == "PdNativeGui":
          
            s += self.getNativeGui(x, self.get(x,'className'))
          
          elif "goparray" == self.get(x,'className'):
          
            s += "#X array"
            s += ' ' + self.get(x,'name')
            s += ' ' + str(self.get(x,'size'))
            s += ' float'
            s += ' ' + str(GOPArrayFlags.index(self.get(x,'flag')))
          
          else:
          
            # TODO
            # IEMGUI stuff
            # more granular control on each param
            className = self.get(x,'className')
            s += "#X obj"
            s += ' ' + str(self.get(x,'position','x'))
            s += ' ' + str(self.get(x,'position','y'))
            s += ' ' + className
            
            if self.get(x, "__pdpy__") == 'PdIEMGui':
              # log(1,x)
              # s += ' ' + ' '.join(get(x,'args'))
              
              rcv = self.get(x,'receive') if hasattr(x,'receive') else 'empty'
              snd = self.get(x,'send') if hasattr(x,'send') else 'empty'
              lbl = self.get(x,'label') if hasattr(x,'label') else 'empty'
              xof = str(self.get(x,'offset', 'x')) if hasattr(x,'offset') else None
              yof = str(self.get(x,'offset', 'y')) if hasattr(x,'offset') else None
              lff = str(self.get(x,'font', 'face')) if hasattr(x,'font') else None
              lfs = str(self.get(x,'font', 'size')) if hasattr(x,'font') else None
              lbc = str(self.get(x,'lbcolor')) if hasattr(x,'lbcolor') else None
              bgc = str(self.get(x,'bgcolor')) if hasattr(x,'bgcolor') else None
              fgc = str(self.get(x,'fgcolor')) if hasattr(x,'fgcolor') else None

              if "vu" == className:
                s+=f" {str(self.get(x,'area','width'))} {str(self.get(x,'area','height'))}"
                s+=f" {rcv} {lbl}"
                s+=f" {'-1' if xof is None else xof}"
                s+=f" {'-8' if yof is None else yof}"
                s+=f" {'0' if lff is None else lff}"
                s+=f" {'10' if lfs is None else lfs}"
                s+=f" {'-66577' if bgc is None else bgc}"
                s+=f" {'-1' if lbc is None else lbc}"
                if hasattr(x,'scale'):
                  s+=f" {'1' if self.get(x,'scale') else '1'}"
                else:
                  s+= ' 1'
                if hasattr(x,'flag'):
                  s+=f" {'1' if self.get(x,'flag') else '0'}"
                else:
                  s+= ' 0'
              
              elif "tgl" == className:
                # log(1,"TGL",x)
                s+=f" {str(self.get(x,'size'))}"
                s+=f" {'1' if self.get(x,'init') else '0'}"
                s+=f" {snd} {rcv} {lbl}"
                s+=f" {'17' if xof is None else xof}"
                s+=f" {'7' if yof is None else yof}"
                s+=f" {'0' if lff is None else lff}"
                s+=f" {'10' if lfs is None else lfs}"
                s+=f" {'-262144' if bgc is None else bgc}"
                s+=f" {'-1' if fgc is None else fgc}"
                s+=f" {'-1' if lbc is None else lbc}"
                s+=f" {'1' if self.get(x,'flag') else '0'}"
                s+=f" {str(self.get(x,'nonzero',default='1'))}"
                # log(1,s)

              elif "cnv" == className or "my_canvas" == className:
                s+=f" {str(self.get(x,'size',default='15'))}"
                s+=f" {str(self.get(x,'area','width'))} {str(self.get(x,'area','height'))}"
                s+=f" {snd} {rcv} {lbl}" if snd is not None else f" {rcv} {lbl}"
                s+=f" {'20' if xof is None else xof}"
                s+=f" {'12' if yof is None else yof}"
                s+=f" {'0' if lff is None else lff}"
                s+=f" {'14' if lfs is None else lfs}"
                s+=f" {'-233017' if bgc is None else bgc}"
                s+=f" {'-66577' if lbc is None else lbc}"
                s+=f" {'1' if self.get(x,'flag') else '0'}"

              elif "radio" in className or 'rdb' == className:
                s+=f" {str(self.get(x,'size'))} {str(self.get(x,'flag'))}"
                s+=f" {'1' if self.get(x,'init') else '0'} {str(self.get(x,'number'))}"
                s+=f" {snd} {rcv} {lbl}"
                s+=f" {'0' if xof is None else xof}"
                s+=f" {'-8' if yof is None else yof}"
                s+=f" {'0' if lff is None else lff}"
                s+=f" {'10' if lfs is None else lfs}"
                s+=f" {'-262144' if bgc is None else bgc}"
                s+=f" {'-1' if fgc is None else fgc}"
                s+=f" {'-1' if lbc is None else lbc}"
                s+=f" {str(self.get(x,'value'))}"

              elif "bng" == className:
                s+=f" {str(self.get(x,'size'))} {str(self.get(x,'hold'))}"
                s+=f" {str(self.get(x,'intrrpt'))} {'1' if self.get(x,'init') else '0'}"
                s+=f" {snd} {rcv} {lbl}"
                s+=f" {'17' if xof is None else xof}"
                s+=f" {'7' if yof is None else yof}"
                s+=f" {'0' if lff is None else lff}"
                s+=f" {'10' if lfs is None else lfs}"
                s+=f" {'-262144' if bgc is None else bgc}"
                s+=f" {'-1' if fgc is None else fgc}"
                s+=f" {'-1' if lbc is None else lbc}"

              elif "nbx" == className:
                s+=f" {str(self.get(x,'digit_width'))} {str(self.get(x,'height'))}"
                s+=f" {str(self.get(x,'limits', 'lower'))}"
                s+=f" {str(self.get(x,'limits', 'upper'))}"
                s+=f" {'1' if self.get(x,'log_flag') else '0'} {'1' if self.get(x,'init') else '0'}"
                s+=f" {snd} {rcv} {lbl}"
                s+=f" {'0' if xof is None else xof}"
                s+=f" {'-8' if yof is None else yof}"
                s+=f" {'0' if lff is None else lff}"
                s+=f" {'10' if lfs is None else lfs}"
                s+=f" {'-262144' if bgc is None else bgc}"
                s+=f" {'-1' if fgc is None else fgc}"
                s+=f" {'-1' if lbc is None else lbc}"
                s+=f" {str(self.get(x,'value'))}"
                s+=f" {str(self.get(x,'log_height'))}"
              
              elif "hsl" == className:
                s+=f" {str(self.get(x,'area','width'))} {str(self.get(x,'area','height'))}"
                s+=f" {str(self.get(x,'limits', 'lower'))}"
                s+=f" {str(self.get(x,'limits', 'upper'))}"
                s+=f" {'1' if self.get(x,'log_flag') else '0'}"
                s+=f" {'1' if self.get(x,'init') else '0'}"
                s+=f" {snd} {rcv} {lbl}"
                s+=f" {'-2' if xof is None else xof}"
                s+=f" {'-8' if yof is None else yof}"
                s+=f" {'0' if lff is None else lff}"
                s+=f" {'10' if lfs is None else lfs}"
                s+=f" {'-262144' if bgc is None else bgc}"
                s+=f" {'-1' if fgc is None else fgc}"
                s+=f" {'-1' if lbc is None else lbc}"
                s+=f" {str(self.get(x,'value'))}"
                s+=f" {'1' if self.get(x,'steady') else '0'}"
              
              elif "vsl" == className:
                s+=f" {str(self.get(x,'area','width'))} {str(self.get(x,'area','height'))}"
                s+=f" {str(self.get(x,'limits', 'lower'))}"
                s+=f" {str(self.get(x,'limits', 'upper'))}"
                s+=f" {'1' if self.get(x,'log_flag') else '0'} {'1' if self.get(x,'init') else '0'}"
                s+=f" {snd} {rcv} {lbl}"
                s+=f" {'0' if xof is None else xof}"
                s+=f" {'-9' if yof is None else yof}"
                s+=f" {'0' if lff is None else lff}"
                s+=f" {'10' if lfs is None else lfs}"
                s+=f" {'-262144' if bgc is None else bgc}"
                s+=f" {'-1' if fgc is None else fgc}"
                s+=f" {'-1' if lbc is None else lbc}"
                s+=f" {str(self.get(x,'value'))}"
                s+=f" {'1' if self.get(x,'steady') else '0'}"
              
              else:
                log(2,"Can't parse PdIEMGui", x)

            
            else:
              
              if hasattr(x, "subclass"):
                s += ' ' + self.get(x,'subclass')
              
              if hasattr(x, "keep"):
                if self.get(x,'keep'):
                  s += ' -k' 

              if hasattr(x, "name"):
                s += ' ' + self.get(x,'name')
              
              if hasattr(x, "size"):
                s += ' ' + str(self.get(x,'size'))

              if hasattr(x, "data"):
                haso = True
                
              if hasattr(x,"args"):
                args = self.get(x,'args')
                # print("ARGUMENTS",args,type(args))
                if isinstance(args, list):
                  s += ' ' + ' '.join(args)
                else:
                  s += args
          
          
          self.getBorder(x)  

        if haso:
          
          s = "#A"
          
          if "text" == self.get(x,'className'):
            s += ' set'
          else:
            s += ' saved'
          
          for e in self.get(x,'data'):
          
            if isinstance(e, str):
              s += ' ' + e #+ " \\;"
          
            elif isinstance(e, list):
              s += ' ' + ' '.join(e) + " \\;"
          
            else:
              s += ' ' + str(e)
          
          
          haso = False

  def getDeclare(self, kind):
    if hasattr(self.obj, kind):
      declares = ET.SubElement(self.et, 'declare')
      for x in self.get(self.obj, kind):
        ET.SubElement(declares, kind[:-1]).text = x
      

  def getDependencies(self):
    """ Parses the dependencies entry into paths and libs using `getDeclare()` """
    if hasattr(self.obj, "dependencies"):
      self.getDeclare(self.get(self.obj,'dependencies'), 'paths')
      self.getDeclare(self.get(self.obj,'dependencies'), 'libs')

  def getRestore(self):
    # Get the self.depth and remove the last element
    
    self.depth.pop()
    
    if hasattr(self.obj, 'position'):
      ET.SubElement(self.et, 'xpos').text = self.get(self.obj,'position','x')
      ET.SubElement(self.et, 'ypos').text = self.get(self.obj,'position','y')
      ET.SubElement(self.et, 'title').text = self.get(self.obj,'title')
      

  def getBorder(self,x):
    if hasattr(x, 'border'):
      print("border in", x)
      # ET.SubElement(mgn, 'x').text = print("border")
      # self.out.append(f"#X f {str(self.get(obj,'border'))} ;\r\n")

  def getCoords(self):
    if hasattr(self.obj, 'coords'):
      coords = ET.SubElement(self.et, 'coords')

      a = ET.SubElement(coords, 'a')
      b = ET.SubElement(coords, 'b')
      ET.SubElement(a, 'xpos').text = self.get(self.get(self.obj,'coords','range'),'a','x')
      ET.SubElement(b, 'xpos').text = self.get(self.get(self.obj,'coords','range'),'b','x')
      ET.SubElement(a, 'ypos').text = self.get(self.get(self.obj,'coords','range'),'a','y')
      ET.SubElement(b, 'xpos').text = self.get(self.get(self.obj,'coords','range'),'b','y')

      ET.SubElement(coords, 'width').text = self.get(self.get(self.obj,'coords','dimension'),'width')
      ET.SubElement(coords, 'height').text = self.get(self.get(self.obj,'coords','dimension'),'height')
      
      ET.SubElement(coords, 'gop').text = self.get(self.obj,'coords','gop')
      
      if hasattr(self.get(self.obj,'coords'), 'margin'):
        mgn = ET.SubElement(coords, 'margin')
        ET.SubElement(mgn, 'x').text = self.get(self.get(self.obj,'coords','margin'),'x')
        ET.SubElement(mgn, 'y').text = self.get(self.get(self.obj,'coords','margin'),'y')
      

  def getCanvas(self, x, root=False):
    # Get the self.depth and add a new element with -1
    
    self.depth.append(-1)
    
    cnv = ET.SubElement(self.et, 'canvas')
    ET.SubElement(cnv, 'xpos').text = self.get(x,'screen','x')
    ET.SubElement(cnv, 'ypos').text = self.get(x,'screen','y')
    ET.SubElement(cnv, 'width').text = self.get(x,'dimension','width')
    ET.SubElement(cnv, 'height').text = self.get(x,'dimension','height')
    # Do not add name and vis flag if it is the root, add font instead
    if root:
      ET.SubElement(cnv, 'font').text = str(self.get(x,'font'))
    else:
      ET.SubElement(cnv, 'name').text = self.get(x,'name')
      ET.SubElement(cnv, 'vis').text = 1 if self.get(x,'vis') else 0
    
    # recurse through the nodes if it is not the root
    if not root:
      self.getNodes()
      self.getComments()
      self.getConnections()
      self.getCoords()
      self.getRestore()
      self.getBorder()

  def getNativeGui(self, x, kind):
    cnv = ET.SubElement(self.et, kind)
    
    ET.SubElement(cnv,'xpos').text = int(self.get(x,'position','x'))
    ET.SubElement(cnv,'ypos').text = int(self.get(x,'position','y'))

    if hasattr(x, "digit_width"):
      ET.SubElement(cnv,'digit-width').text = int(self.get(x,'digit_width'))

    if hasattr(x, "limits"):
      ET.SubElement(cnv,'lower').text = int(self.get(x,'limits','lower'))
      ET.SubElement(cnv,'upper').text = int(self.get(x,'limits','upper'))

    if hasattr(x, "flag"):
      ET.SubElement(cnv,'flag').text = int(self.get(x,'flag'))
    
    if hasattr(x, "label"):
      ET.SubElement(cnv,'label').text = self.get(x,'label')

    if hasattr(x, "receive"):
      ET.SubElement(cnv,'receive').text = self.get(x,'receive')

    if hasattr(x, "send"):
      ET.SubElement(cnv,'send').text = self.get(x,'send')

    
