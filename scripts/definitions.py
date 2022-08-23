# LAYER 1 ===============================================================
class Base(object): pass
class CanvasBase(object): pass
class Default(object): pass
class XmlTagConvert(object): pass
class ArgumentException(Exception): pass
class PdPyEncoder(JSONEncoder): pass

# LAYER 2 ===============================================================
class Area(Base): pass
class Scalar(Base): pass
class Size(Base): pass
class Point(Base): pass
class Iolet(Base): pass
class Struct(Base): pass
class Bounds(Base): pass
class Comment(Base): pass
class Coords(Base): pass
class Comm(Base): pass
class Data(Base): pass
class Dependencies(Base): pass
class Edge(Base): pass
class Graph(Base): pass
class Translator(Base): pass
class IEMFont(Base): pass
class IEMLabel(Base): pass
class List(Base): pass
class Msg(Base): pass
class PdGOPArray(Base): pass
# DUAL INHERITANCE
class PdPy(CanvasBase, Base): pass
class Canvas(CanvasBase, Base): pass
# CLASSES FROM WHICH OTHER CLASSES ARE DERIVED
class Float(Base): pass
class Obj(Base): pass

# LAYER 3 =====================================================================
class Symbol(Float): pass
class Message(Obj): pass
class Gui(Obj): pass
# FROM DUAL INHERITANCE
class PdPyParser(PdPy): pass
# CLASSES FROM WHICH OTHER CLASSES ARE DERIVED
class Object(Obj): pass

# LAYER 4 =====================================================================
# ALL DERIVE FROM OBJECT
class Array(Object): pass
class Bng(Object): pass
class Cnv(Object): pass
class Nbx(Object): pass
class Radio(Object): pass
class Slider(Object): pass
class Toggle(Object): pass
class Vu(Object): pass
