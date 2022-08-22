Libpd
=====

Here you can learn how to run Pd patches with ``pdpy``.
The code we'll execute is here:

.. code-block:: python
  :linenos:

  from pdpy import Patch, Obj

  with Patch(name="mypatch", root=True) as p:
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


.. note::

  For ``libpd`` to work, it has to be installed and available on your python environment. 
  
Instructions
------------

clone the libpd repository::
    
    git clone http://github.com/libpd/libpd.git
    cd libpd
    git submodule update --init --recursive


Then, type make::

    make


Once compiled, head to the python directory and make again::

    cd python
    make


If everything compiled correctly, you should now source your venv and install::

    source ~/.pdpy/bin/activate 
    pip install -e .


That's it, you should be able to do::

    python
    >>> import pylibpd


.. note::

  Head to `<https://github.com/libpd/libpd/wiki/Python-API>`_ for more information.


