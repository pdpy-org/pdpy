Additive Synthesis
==================

In this example we see how to create a harmonic spectrum using additive synthesis.
The code is displayed first in full, then it is explained in detail.

.. code-block:: python
  :linenos:

  from pdpy import PdPy, Obj                  # necessary imports
  fund = 110                                  # fundamental frequency in Hz 
  partials = 8                                # number of partials
  mypatch = PdPy(name="additive", root=True)  # initialize a patch
  dac = Obj('dac~')                           # instantiate a ``dac~`` object
  mypatch.create(dac)                         # creates the dac on the canvas
  for i in range(1, partials):                # loop through all partials
    objects = [                               # put objects on a list
      Obj("osc~").addargs(fund * i),          # a sinusoid at the partial's freq
      Obj("*~").addargs(1 / partials)         # brute normalization
    ]
    mypatch.create(*objects)                  # create the objects list
    mypatch.connect(*objects)                 # connect it
    mypatch.connect(objects[-1], [dac, 0, 1]) # connect ``*~`` to dac chans 1,2
  mypatch.write()                             # write the patch out


First, we import the library so we can use it::

  from pdpy import PdPy, Obj

Variables
---------

Now, we can define some variables.
**fund** will have the fundamental frequency in Hz, 
and **npartials** will store the number of partials to create::

  fund = 110
  npartials = 8


`dac~` Object
-------------

The next three lines define a PdPy patch and creates a `dac~` object::

  mypatch = PdPy(name="additive", root=True)
  dac = Obj('dac~')
  mypatch.create(dac)                         


.. note::
  
  We create a `dac~` object first so we can connect all the partials to it.


Partials
--------

Each partial will be made of a single sinusoid.
For this, we need an oscillator object `osc~` connected to a multiplier `*~`.
Since we need **npartials** number of partials, in this case ``8``, we iterate::

  for i in range(1, npartials):

Within this iteration, we build an **objects** list with the two objects::

  objects = [
    Obj("osc~").addargs(fund * i),
    Obj("*~").addargs(1 / npartials)
  ]

.. note::
  
  1. The :func:`addargs` function of the `osc~` object is passed the **fund** variable multiplied by the partial number **i**, which is the required for a harmonic spectrum.
  2. The :func:`addargs` function of the `*~` object is passed the coefficient to normalize (average) **n** number of partials, ie. ``1 / n``.


Then, still in the loop, we create and connect the objects together::

  mypatch.create(*objects)
  mypatch.connect(*objects)


Before exiting the loop, we connect the last object `*~` to both inlets of the `dac~`::

  mypatch.connect(objects[-1], [dac, 0, 1])


To finish this patch, you need to write it to disk::

  mypatch.write()


You should now see an `additive.pd` patch on the working directory.

