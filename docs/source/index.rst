****
pdpy
****

``pdpy`` is a python package that allows you to make and edit Pure Data (Pd) patches directly from python code.
You can also translate Pd files to other container files such as json, pickle, or xml.
The core library consists of a set of :doc:`classes`, plus some utility functions.

.. hint::
  For example, the :class:`pdpy_lib.patching.patch.Patch` class allows you to run the newly created patch using the embedded Pd engine ``libpd``.
  See the :doc:`examples/libpd` example for more.

.. note::
  This project is under active development. PRs are welcome!



References
----------

This project is inspired by many discussions and projects:

* Pure Data to XML: see `this discussion <https://lists.puredata.info/pipermail/pd-dev/2004-12/003316.html>`_ on the pd-list archives.
* Pure Data to JSON: see `this other one <https://lists.puredata.info/pipermail/pd-dev/2012-06/018434.html>`_ on the pd-list archives.
* Pure Data file format specifications were expained `here <http://puredata.info/docs/developer/PdFileFormat>`_
* *New* Pd file format `discussion <https://lists.puredata.info/pipermail/pd-dev/2007-09/009483.html>`_ on the pd-list archives.
* ``sebpiq``'s repostirories: `WebPd_pd-parser <https://github.com/sebpiq/WebPd_pd-parser>`_, as well as his `pd-fileutils <https://github.com/sebpiq/pd-fileutils>`_
* ``dylanburati``'s `puredata-compiler <https://github.com/dylanburati/puredata-compiler>`_


Copyright
---------

* `libpd <https://github.com/libpd/libpd>`_: Copyright (c) Peter Brinkmann & the libpd team 2010-2021
* `Pure Data <https://github.com/pure-data/pure-data>`_: Copyright (c) 1997-2021 Miller Puckette and others.
* `pyaudio <https://people.csail.mit.edu/hubert/pyaudio>`_: Copyright (c) 2006 Hubert Pham 

Donate
------

If you feel like helping this project, please donate `over here <https://www.paypal.com/donate/?business=B5TMA7FZ4BXA2&no_recurring=0&currency_code=USD>`_, or by clicking the following button:

|donate|_

.. |donate| image:: https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif
.. _donate: https://www.paypal.com/donate/?business=B5TMA7FZ4BXA2&no_recurring=0&currency_code=USD







.. toctree::
  :caption: Getting Started
  :maxdepth: 1

  installation
  usage
  virtual_env
  install_libpd

.. toctree::
  :caption: Examples
  :maxdepth: 1
  
  examples/holamundo
  examples/simpleaudio
  examples/additive_synthesis
  examples/translation
  examples/connections
  examples/contexts
  examples/arrays
  examples/libpd
  examples/comments



.. toctree::
  :caption: API Documentation
  :maxdepth: 2
  
  overview
  classes
