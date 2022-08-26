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
    pdpy_lib.objects.obj.Obj
    pdpy_lib.objects.msg.Msg
    pdpy_lib.objects.gui.Gui
    pdpy_lib.objects.comment.Comment

IEMGui
------

.. autosummary::
  
    pdpy_lib.iemgui.toggle.Toggle
    pdpy_lib.iemgui.bng.Bng
    pdpy_lib.iemgui.nbx.Nbx
    pdpy_lib.iemgui.slider.Slider
    pdpy_lib.iemgui.radio.Radio
    pdpy_lib.iemgui.vu.Vu
    pdpy_lib.iemgui.cnv.Cnv
    pdpy_lib.iemgui.iemlabel.IEMLabel
    pdpy_lib.iemgui.iemfont.IEMFont

Memory
------

.. autosummary::

    pdpy_lib.memory.types.Float
    pdpy_lib.memory.types.Int
    pdpy_lib.memory.types.Symbol
    pdpy_lib.memory.types.List
    pdpy_lib.memory.data.Data
    pdpy_lib.memory.scalar.Scalar
    pdpy_lib.memory.struct.Struct
    pdpy_lib.memory.array.Array
    pdpy_lib.memory.goparray.GOPArray
    pdpy_lib.memory.graph.Graph


Patching
--------

.. autosummary::
      
    pdpy_lib.patching.patch.Patch
    pdpy_lib.patching.pdpy.PdPy
    pdpy_lib.patching.canvas.Canvas
    pdpy_lib.patching.dependencies.Dependencies
    pdpy_lib.patching.comm.Comm

Connections
-----------

.. autosummary::
  
    pdpy_lib.connections.edge.Edge
    pdpy_lib.connections.iolet.Iolet

Extra
-----

.. autosummary::
  
    pdpy_lib.extra.arranger.Arranger
    pdpy_lib.extra.translator.Translator


Primitives
----------

.. autosummary::

    pdpy_lib.primitives.point.Point
    pdpy_lib.primitives.size.Size
    pdpy_lib.primitives.area.Area
    pdpy_lib.primitives.bounds.Bounds
    pdpy_lib.primitives.coords.Coords


Core
----

.. autosummary::

    pdpy_lib.core.base.Base
    pdpy_lib.core.canvasbase.CanvasBase
    pdpy_lib.core.object.Object
    pdpy_lib.core.message.Message


Utilities
---------

.. autosummary::

    pdpy_lib.utilities.namespace.Namespace
    pdpy_lib.utilities.default.Default
    pdpy_lib.utilities.exceptions.ArgumentException
    pdpy_lib.utilities.exceptions.MalformedName
    pdpy_lib.utilities.utils
    pdpy_lib.utilities.regex

Encoding
--------

.. autosummary::
    
    pdpy_lib.encoding.pdpyencoder.PdPyEncoder
    pdpy_lib.encoding.xmltagconvert.XmlTagConvert
    pdpy_lib.encoding.xmlbuilder.XmlBuilder


Parsing
-------

.. autosummary::

    pdpy_lib.parse.pdpyxmlparser.PdPyXMLParser
    pdpy_lib.parse.pdpyparser.PdPyParser
    pdpy_lib.parse.pdpy2json

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
