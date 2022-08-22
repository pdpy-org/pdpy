Arrays
======

Here you can learn how to create arrays in ``pdpy``.
The code we'll execute is here:

.. code-block:: python
  :linenos:

  import pdpy
  import math
  with pdpy.PdPy(name='arrays', root=True) as pd:
    for _ in range(3):
      pd.createArray()
    pd.createArray(name="myarray", length=123)
    pd.createArray(name="keeping", length=100, keep=True, data=[1/i**2 for i in range(-50,50) if i != 0])
    pd.createGOPArray()


Import
------

First, we import pdpy, the math module (see below), and create a PdPy context::

  import pdpy
  import math
  with pdpy.PdPy(name='arrays', root=True) as pd:


Array-define subclass
---------------------

To create an array, run PdPy's ``createArray`` method.
In this case, we are creating three::

  for _ in range(3):
    pd.createArray()


.. note::

  If no name is provided, the arrays are named like in pd: ``arrayN``


Properties
----------

Here, we create an array and pass a ``name`` and the ``length`` properties::

  pd.createArray(name="myarray", length=123)


Data
----

We can make some data to feed the array.
Let's make a sinewave::
  
  sinewave = [ math.cos( i / 100 * 2 * math.pi) for i in range(100) ]


There are more properties you can pass to an array, including a data list.
In the following line, we set ``keep`` to ``True``, so that the data is kept infile::
  
  pd.createArray(name="keeping", length=100, keep=True, data=sinewave)



Graph-on-parent
---------------

We can also create Graph-on-parent (GOP) array, and pass other data to it::
  
  pd.createGOPArray(data = map(lambda x,y: x * y**2, sinewave, sinewave))


