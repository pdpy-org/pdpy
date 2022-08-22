Virtual Environment
===================

It is recommended to use ``pdpy`` within a virtual environment.
To set a virtual environment with ``python3``, you can follow this instructions.


Create
------


To start, you need to create the virtual environment.
You only need to do this once; you can reuse your ``venv`` later on.
For this, you need a path to a common folder.
The examples in this documentation use ``~/.pdpy`` as a default path::
    
    python3 -m venv ~/.pdpy


Source
------

To use your virtual envirnoment, you need to ``source`` it on your terminal.
You do this with the following command::

    source ~/.pdpy/bin/activate


The terminal window should read something like this::

   (.pdpy) user:dir user$



Installing
----------

The next thing you'd want to do is install the necessary packages to your ``venv``, for example::

    pip install pyaudio

Head to :doc:`install_libpd` to see how install ``libpd`` to your environment.
