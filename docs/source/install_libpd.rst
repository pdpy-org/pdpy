Installing LibPd
================

clone the libpd repository::
    
    git clone http://github.com/libpd/libpd.git
    cd libpd
    git submodule update --init --recursive


Make sure you have the correct build tools. 
Check the README.md file. 
Then, type make::

    make


Once compiled, head to the python directory and make again::

    cd python
    make


If everything compiled correctly, you should now source your venv and install::

    source ~/.pdpy/bin/activate 
    pip install -e .


.. note::

  Head to :doc:`virtual_env` for some instructions on how to make your virtual environment.


That's it, you should be able to do::

    python
    >>> import pylibpd


.. note::

  Head to `<https://github.com/libpd/libpd/wiki/Python-API>`_ for more information.


