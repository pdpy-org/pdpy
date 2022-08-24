#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
""" 
API Overview
============

Objects
-------

.. autosummary::
    pdpy.objects.obj.Obj
    pdpy.objects.msg.Msg
    pdpy.objects.gui.Gui
    pdpy.objects.comment.Comment

IEMGui
------

.. autosummary::
  
    pdpy.iemgui.toggle.Toggle
    pdpy.iemgui.bng.Bng
    pdpy.iemgui.nbx.Nbx
    pdpy.iemgui.slider.Slider
    pdpy.iemgui.radio.Radio
    pdpy.iemgui.vu.Vu
    pdpy.iemgui.cnv.Cnv
    pdpy.iemgui.iemlabel.IEMLabel
    pdpy.iemgui.iemfont.IEMFont

Memory
------

.. autosummary::

    pdpy.memory.types.Float
    pdpy.memory.types.Int
    pdpy.memory.types.Symbol
    pdpy.memory.types.List
    pdpy.memory.data.Data
    pdpy.memory.scalar.Scalar
    pdpy.memory.struct.Struct
    pdpy.memory.array.Array
    pdpy.memory.goparray.GOPArray
    pdpy.memory.graph.Graph


Patching
--------

.. autosummary::
      
    pdpy.patching.patch.Patch
    pdpy.patching.pdpy.PdPy
    pdpy.patching.canvas.Canvas
    pdpy.patching.dependencies.Dependencies
    pdpy.patching.comm.Comm

Connections
-----------

.. autosummary::
  
    pdpy.connections.edge.Edge
    pdpy.connections.iolet.Iolet

Extra
-----

.. autosummary::
  
    pdpy.extra.arranger.Arranger
    pdpy.extra.translator.Translator


Primitives
----------

.. autosummary::

    pdpy.primitives.point.Point
    pdpy.primitives.size.Size
    pdpy.primitives.area.Area
    pdpy.primitives.bounds.Bounds
    pdpy.primitives.coords.Coords


Core
----

.. autosummary::

    pdpy.core.base.Base
    pdpy.core.canvasbase.CanvasBase
    pdpy.core.object.Object
    pdpy.core.message.Message


Utilities
---------

.. autosummary::

    pdpy.utilities.namespace.Namespace
    pdpy.utilities.default.Default
    pdpy.utilities.exceptions.ArgumentException
    pdpy.utilities.exceptions.MalformedName
    pdpy.utilities.utils
    pdpy.utilities.regex

Encoding
--------

.. autosummary::
    
    pdpy.encoding.pdpyencoder.PdPyEncoder
    pdpy.encoding.xmltagconvert.XmlTagConvert
    pdpy.encoding.xmlbuilder.XmlBuilder


Parsing
-------

.. autosummary::

    pdpy.parse.pdpyxmlparser.PdPyXMLParser
    pdpy.parse.pdpyparser.PdPyParser
    pdpy.parse.pdpy2json

"""

from .core.base import *
from .core.canvasbase import *
from .core.object import *
from .core.message import *
from .primitives.point import *
from .primitives.size import *
from .primitives.area import *
from .primitives.bounds import *
from .primitives.coords import *
from .objects.comment import *
from .objects.obj import *
from .objects.msg import *
from .objects.gui import *
from .iemgui.iemfont import *
from .iemgui.iemlabel import *
from .iemgui.bng import *
from .iemgui.cnv import *
from .iemgui.nbx import *
from .iemgui.radio import *
from .iemgui.slider import *
from .iemgui.toggle import *
from .iemgui.vu import *
from .memory.data import *
from .memory.scalar import *
from .memory.array import *
from .memory.struct import *
from .memory.goparray import *
from .memory.graph import *
from .memory.types import *
from .patching.pdpy import *
from .patching.patch import *
from .patching.canvas import *
from .patching.dependencies import *
from .patching.comm import *
from .encoding.pdpyencoder import *
from .encoding.xmltagconvert import *
from .encoding.xmlbuilder import *
from .utilities.utils import *
from .utilities.regex import *
from .utilities.namespace import *
from .utilities.default import *
from .utilities.exceptions import *
from .parse.pdpy2json import *
from .parse.pdpyxmlparser import *
from .parse.pdpyparser import *
from .connections.edge import *
from .connections.iolet import *
from .extra.arranger import *
from .extra.translator import *
