Libpd
=====

Here you can learn how to run Pd patches with ``pdpy``.
The code we'll execute is here:

.. code-block:: python
  :linenos:

  from pdpy import Patch, Obj
  with Patch(name="mypatch", root=True, callback=False) as p:
    osc = [Obj('osc~').addargs(110 * i) for i in range(1, 16)]
    mul = Obj('*~').addargs(1/16)
    dac = Obj('dac~')
    p.create(*osc, dac, mul)
    for o in osc: p.connect(o, mul)
    p.connect(mul, [dac, 0, 1])
  

Patch
-----

This class allows you to create a patch within a context.
Once the context exits, the patch is automatically executed using ``libpd``.


First, we import pdpy::
  
  from pdpy import Patch, Obj


Then, we enter the :class:`Patch` context as ``root`` and we name it::

  with Patch(name="mypatch", root=True) as p:


Next, we create some objects.
The following line creates 16 harmonics with a fundamental at 110 Hz::

    osc = [Obj('osc~').addargs(110 * i) for i in range(1, 16)]


Now, we multiply the partials so they are brutely normalized.
We also need a dac object to output all of the partials::

    mul = Obj('*~').addargs(1/16)
    dac = Obj('dac~')


Finally, we create all objects, and we connect them.
Notice how we connect all ``osc`` objects to the multiplier, and the multiplier to both channels of the dac object::

    p.create(*osc, dac, mul)
    for o in osc: p.connect(o, mul)
    p.connect(mul, [dac, 0, 1])


You should hear a harmonic spectrum coming out of the speakers when you run::

  python examples/libpd.py


.. note::

  For ``libpd`` to work, it has to be installed and available on your python environment. See :doc:`../install_libpd`


.. note::

  You also need to have ``pyaudio`` installed.
  You can install it to your virtual environment with ``pip``::
    
    pip install pyaudio

