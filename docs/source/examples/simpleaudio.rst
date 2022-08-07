Simple Audio
============

Here you can learn how to make a simple Pure Data audio patch with **pdpy**. 

This patch send out a sinusoid at 440 ``osc~ 440``, 
with amplitude 0.01 ``*~ 0.01``, 
to channels #1, #3 and #4 of the system audio ``dac~ 1 2 3 4``

.. code-block:: python
  :linenos:
  
  from pdpy import PdPy, Obj                      # necesary imports
  mypatch = PdPy(name="simpleaudio", root=True)   # initialize
  obj1 = Obj('osc~').addargs(440)                 # an ``osc~`` at 440 Hz
  obj2 = Obj('*~').addargs(0.01)                  # a signal multiplier at 0.01
  obj3 = Obj('dac~').addargs([1, 2, 3, 4])        # a 4-channel ``dac~``
  mypatch.create(obj1, obj2, obj3)                # create them in the patch
  mypatch.connect(obj1, obj2)                     # connect ``osc~`` to ``*~``
  mypatch.connect(obj2, [obj3, 0, 2, 3])          # connect ``*~`` chans 1,3,4
  mypatch.write()                                 # write out the patch
  
The logic of lines 1-6 and 8 is similar to :doc:`holamundo`. 
Please refer to that example for an overview. 
The thing to notice here is the connections in lines 7 and 8.

Connections
-----------

In line 7, the ``connect`` method is called with ``obj1`` and ``obj2``:

.. code-block:: python

  mypatch.connect(obj1, obj2)

This means that the first outlet of the first object is connected to the first inlet of the second object. 
That is to say, the first (and only) outlet of ``osc~ 440`` is connected to the first inlet of the multiplier ``*~ 0.01``.

In line 8, however, we have a different syntax on the second object:

.. code-block:: python

  mypatch.connect(obj2, [obj3, 0, 2, 3])

What this means is that we are connecting the first outlet of the first object, 
with the 1st, 3rd, and 4th inlets of the second object.
In other words, we connect the first outlet of the multiplier ``*~ 0.01`` to
the ``dac~ 1 2 3 4`` object's inlets 1, 3, and 4. 

.. note::
  When a list is passed to ``mypatch.connect`` the inlet indices start at 0. 
  So, the first inlet is the 0th, the second is the 1st, and so on.

.. note::
  The order does not matter, so we can get the same result calling:
  
  .. code-block:: python

    mypatch.connect(obj2, [obj3, 3, 0, 2])

