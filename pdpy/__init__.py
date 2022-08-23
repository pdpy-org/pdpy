#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2021-22 Fede Camara Halac
# **************************************************************************** #
""" Main inititlization """

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
