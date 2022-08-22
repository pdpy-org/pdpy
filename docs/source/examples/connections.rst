Connections
===========

Here you can learn how to connect and disconnect objects in ``pdpy``.
The code we'll execute is here:


.. code-block:: python
  :linenos:

  import pdpy
  pd = pdpy.PdPy(name='test_disconnect',root=True)
  obj = pdpy.Obj('loadbang')
  printer = pdpy.Obj('print')
  pd.create(obj, printer)
  pd.connect(obj,printer)
  pd.__arrange__(pd)
  print(pd.__pd__())
  pd.disconnect(obj,printer)
  print(pd.__pd__())


First, we import pdpy and create a PdPy instance::

  >>> import pdpy
  >>> pd = pdpy.PdPy(name='test_disconnect',root=True)
  Found  darwin  platform.
  Locating pd...
  Found pd at:  /Applications/Pd-0.52-2.app/Contents/Resources/bin/pd


Then, we create a loadbang and a printer, to test::

  >>> obj = pdpy.Obj('loadbang')
  >>> printer = pdpy.Obj('print')
  >>> pd.create(obj, printer)
  <pdpy.classes.pdpy.PdPy object at 0x106596820>


We connect them, and let's arrange them so that we can print them::
  
  >>> pd.connect(obj,printer)
  >>> pd.__arrange__(pd)
  Initialized Arrange graph placing algorithm.
  >>> print(pd.__pd__())
  #N canvas 0 22 450 300 12;
  #X obj 10 10 loadbang;
  #X obj 10 58 print;
  #X connect 0 0 1 0;


Now, try disconnecting them::

  >>> pd.disconnect(obj,printer)
  Disconnected 0


Let's see the result::

  >>> print(pd.__pd__())
  #N canvas 0 22 450 300 12;
  #X obj 10 10 loadbang;
  #X obj 10 58 print;


