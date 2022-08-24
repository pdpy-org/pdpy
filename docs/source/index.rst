****
pdpy
****

``pdpy`` is a python package that allows you to make and edit Pure Data (Pd) patches directly from python code.
You can also translate Pd files to other container files such as json, pickle, or xml.
The core library consists of a set of :doc:`classes`, plus some utility functions.

.. hint::
  For example, the :class:`pdpy.patching.patch.Patch` class allows you to run the newly created patch using the embedded Pd engine ``libpd``.
  See the :doc:`examples/libpd` example for more.

.. note::
  This project is under active development. PRs are welcome!



References
----------

This project is inspired by many discussions and projects:

* Pure Data to XML: see `this discussion <https://lists.puredata.info/pipermail/pd-dev/2004-12/003316.html>`_ on the pd-list archives.
* Pure Data to JSON: see `this other one <https://lists.puredata.info/pipermail/pd-dev/2012-06/018434.html>`_ on the pd-list archives.
* New Pd file format `discussion <https://lists.puredata.info/pipermail/pd-dev/2007-09/009483.html>`_ on the pd-list archives.
* PURE DATA FILE FORMAT specifications were expained `here <http://puredata.info/docs/developer/PdFileFormat>`_
* ``sebpiq``'s repostirories: `WebPd_pd-parser <https://github.com/sebpiq/WebPd_pd-parser>`_, as well as his `pd-fileutils <https://github.com/sebpiq/pd-fileutils>`_


Copyright
---------

* `libpd <https://github.com/libpd/libpd>`_: Copyright (c) Peter Brinkmann & the libpd team 2010-2021
* `Pure Data <https://github.com/pure-data/pure-data>`_: Copyright (c) 1997-2021 Miller Puckette and others.
* `pyaudio <https://people.csail.mit.edu/hubert/pyaudio>`_: Copyright (c) 2006 Hubert Pham 









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
  overview

.. toctree::
  :caption: Examples
  :maxdepth: 1
  
  examples/holamundo
  examples/simpleaudio
  examples/translation
  examples/connections
  examples/arrays
  examples/libpd

