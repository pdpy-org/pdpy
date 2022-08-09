Hola Mundo
==========

Here you can learn how to make a simple Pure Data hello world patch with **pdpy**. 
If you know already how patch in Pd, you can bring this knowledge into action.


This example creates a ``loadbang`` connected to a message 
that prints ``Hola Mundo!`` to the Pd console.
The final code is shown first, then you can see it explained line by line.

.. code-block:: python
  :linenos:

  from pdpy import PdPy, Obj, Msg                # necessary imports
  mypatch = PdPy(name="holamundo", root=True)    # a pdpy root patch
  obj1 = Obj('loadbang')                         # a loadbang object
  obj2 = Obj('print')                            # a print object
  msg1 = Msg('Hola Mundo!')                      # a message box with content 
  mypatch.create(obj1, msg1, obj2)               # create them in the patch
  mypatch.connect(obj1, msg1, obj2)              # connect them in the patch
  mypatch.write()                                # write out the patch

Let's break this into parts:

Import
------

First, you import the necessary pdpy Classes (line 1):

.. code-block:: python
  
  from pdpy import PdPy, Obj, Msg

We will briefly go through these classes in this example.
To find out more about these classes, you can go to :class:`pdpy.classes.pdpy.PdPy`, :class:`pdpy.classes.obj.Obj`, and :class:`pdpy.classes.message.Msg`.

A PdPy patch
------------

The PdPy class contains a representation of a Pure Data patch.
With the ``PdPy`` class we can initialize a pdpy root patch (line 2):

.. code-block:: python

  mypatch = PdPy(name="holamundo", root=True)

The ``name`` keyword argument stores the name of the patch, in this case ``holamundo``. 
Because we want ``mypatch`` to be the ``root`` of our Pure Data patch (or in pd-lingo, the parent canvas), we set it to ``true``. 

There are more keyword arguments available, but we wont need them here.
You can go to :class:`pdpy.classes.pdpy.PdPy` to see it in full.

Objects
-------

With the ``Obj`` class we can instantiate a few objects (lines 3,4).
Notice that we can pass a :class:`str` upon instantiation.
The ``Obj`` instance will represent the Pd object called as such.
We will instantiate them in variables arbitrarily called ``obj1`` and ``obj2``.

.. code-block:: python

  obj1 = Obj('loadbang')
  obj2 = Obj('print')

- ``obj1`` is a pdpy ``Obj`` that represents Pd's ``loadbang`` object,
- ``obj2`` is another pdpy ``Obj`` that represents Pd's ``print`` object.

Message
-------

The ``Msg`` class represents Pd's message box.
As such, it can store multiple messages.
In this case, we only have one message that reads ``Hola Mundo!``. 
We will store it in the variable ``msg1`` (line 5):

.. code-block:: python
  
  msg1 = Msg('Hola Mundo!')


Create
------

We now have an instance of the PdPy class in ``mypatch``, together with
two objects ``obj1`` and ``obj2``, and a message box ``msg1``.
What we need to do now is create these objects within the PdPy class. 
We can do that in this way (line 6):

.. code-block:: python

  mypatch.create(obj1, msg1, obj2)

.. note::
  There are other ways of creating objects, for example:
  
  .. code-block:: python
    :linenos:

    mypatch.create(obj1)
    mypatch.create(msg1)
    mypatch.create(obj2)

  Or, we pass a python list to the create function, this way:
  
  .. code-block:: python
    :linenos:

    myobjects = [obj1, msg1, obj2]
    mypatch.create(*myobjects) # notice the expansion * char before the list

  In any case, we have keep them in variables to be able to call them later.

Connect
-------

Once the objects are created, we need to connect them. 
We use the ``connect`` method to do this (line 7):

.. code-block:: python

  mypatch.connect(obj1, msg1, obj2)

.. note::
  If we reuse our ``myobjects`` list above, we can connect objects this way:
  
  .. code-block:: python
    :linenos:

    mypatch.connect(*myobjects)

Write
-----

Finally, we can write the patch to disk. 
We do this with the ``write`` method (line 8):

.. code-block:: python

  mypatch.write()

After writing the patch, you should be able to find a ``holamundo.pd`` file 
in the same directory you were running the python code.

