****
pdpy
****

``pdpy`` is a python package that allows you to make and edit Pure Data (Pd) patches directly from python code.
You can also translate Pd files to other container files such as json, pickle, or xml.
The core library consists of a set of :doc:`classes`, plus some utility functions.
For example, the :class:`pdpy.classes.patch.Patch` class allows you to run the newly created patch using the embedded Pd engine :doc:`examples/libpd`.
You can get libpd from `<http://github.com/libpd>`_.


.. note::
  This project is under active development. PRs are welcome!

.. toctree::
  :caption: Getting Started
  :maxdepth: 1

  installation
  usage
  virtual_env
  install_libpd


.. toctree::
  :caption: Documentation
  :maxdepth: 2
  
  classes

.. toctree::
  :caption: Examples
  :maxdepth: 1
  
  examples/holamundo
  examples/simpleaudio
  examples/translation
  examples/connections
  examples/arrays
  examples/libpd

