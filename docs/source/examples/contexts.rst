Using Python Contexts
=====================

In this example, we see how to use the :py:`with` keyword to open the PdPy patch.
When exiting the context, the file is automatically written to disk.
So, there is no need to call :func:`PdPy.write()` at the end.

The patch creates a spectrum of 16 harmonics with phased-out cosine amplitude envelopes 

.. code-block:: python
  :linenos:

  from pdpy import PdPy, Obj, Msg

  fund = 110
  npartials = 16
  partials = [i for i in range(1, npartials)]

  # create the python context
  with PdPy(name="contexts", root=True) as pd:
    
    # create a dac object
    dac = Obj('dac~')
    pd.create(dac)
    
    for n in range(1,npartials):
      # create an envelope
      phasor = Obj('phasor~').addargs(0.25)
      envelope = [
        phasor,
        Obj('-~').addargs(3.14159 / 2.0),
        Obj('cos~'),
        Obj('+~').addargs(1),
        Obj('/~').addargs(2)
      ] 
      pd.create(*envelope)
      pd.connect(*envelope)
      
      # initialize the phasor's phase
      loadbang = Obj('loadbang')
      message = Msg(str(n/npartials))
      pd.create(loadbang, message)
      pd.connect(loadbang, message)
      pd.connect(message, [phasor, 1])
      
      # create a sinusoid
      oscillator = Obj('osc~').addargs(fund * n)
      multiplier = Obj('*~').addargs(1.0 / npartials)
      mult = Obj('*~')
      pd.create(oscillator, multiplier, mult)
      pd.connect(oscillator, multiplier, mult)

      # connect the envelope to the sinusoid's last multiplier
      pd.connect(envelope[-1], [mult, 1])
      
      # connect the last multiplier to this partials' dac
      pd.connect(mult, [dac, n%2])
