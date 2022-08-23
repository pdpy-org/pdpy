#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project: https://github.com/pdpy-org
# Copyright (C) 2022 Fede Camara Halac
# **************************************************************************** #
from pdpy import PdPy, Obj
mypatch = PdPy(name="simpleaudio", root=True)
internals = ['abs_tilde', 'adc', 'alist', 'append', 'bag', 'bang', 'bang_tilde', 'bendin', 'bendout', 'block_tilde', 'bob_tilde', 'bonk_tilde', 'change', 'choice', 'clip', 'clone', 'cos', 'cputime', 'ctlin', 'ctlout', 'curve', 'dac', 'dbtopow_tilde', 'dbtorms_tilde', 'delay', 'drawnumber', 'dspobj_tilde', 'elem', 'env_tilde', 'exp_tilde', 'expr', 'fiddle_tilde', 'ftom_tilde', 'fudiformat', 'fudiparse', 'g_array', 'g_bang', 'g_canvas', 'g_guiconnect', 'g_hradio', 'g_hslider', 'g_mycanvas', 'g_numbox', 'g_scalar', 'g_text', 'g_toggle', 'g_vradio', 'g_vslider', 'g_vumeter', 'get', 'getsize', 'gfxstub', 'gtemplate', 'key', 'libpdreceive', 'line', 'line_tilde', 'list_append', 'list_fromsymbol', 'list_length', 'list_prepend', 'list_split', 'list_store', 'list_tosymbol', 'list_trim', 'loadbang', 'log_tilde', 'loop_tilde', 'lrshift_tilde', 'm_pd', 'makefilename', 'makenote', 'max', 'metro', 'midiin', 'midiout', 'midirealtimein', 'min', 'minus', 'moses', 'mtof_tilde', 'namecanvas', 'netreceive', 'netsend', 'noise', 'notein', 'noteout', 'openpanel', 'osc', 'oscformat', 'oscparse', 'over', 'pack', 'pd_tilde', 'pdcontrol', 'pdfloat', 'pdint', 'pdsymbol', 'pgmin', 'pgmout', 'phasor', 'pipe', 'pique', 'plot', 'plus', 'poly', 'polytouchin', 'polytouchout', 'pow_tilde', 'powtodb_tilde', 'print', 'ptrobj', 'random', 'readsf', 'realtime', 'receive', 'rmstodb_tilde', 'route', 'samplerate_tilde', 'savepanel', 'savestate', 'select', 'send', 'set', 'setsize', 'sig_tilde', 'sigbiquad', 'sigbp', 'sigcatch', 'sigcpole', 'sigczero', 'sigczero_rev', 'sigdelread', 'sigdelwrite', 'sigfft', 'sigframp', 'sighip', 'siglop', 'sigmund_tilde', 'sigreceive', 'sigrfft', 'sigrifft', 'sigrpole', 'sigrsqrt', 'sigrzero', 'sigrzero_rev', 'sigsamphold', 'sigsend', 'sigsqrt', 'sigthrow', 'sigvcf', 'sigvd', 'sigwrap', 'slop_tilde', 'snapshot_tilde', 'soundfiler', 'spigot', 'stdout', 'stripnote', 'swap', 'tabosc4_tilde', 'tabplay_tilde', 'tabread', 'tabread4', 'tabread4_tilde', 'tabread_tilde', 'tabreceive', 'tabsend', 'tabwrite', 'tabwrite_tilde', 'template', 'threshold_tilde', 'timer', 'times', 'touchin', 'touchout', 'trace', 'trigger', 'unpack', 'until', 'value', 'vinlet', 'vline_tilde', 'voutlet', 'vsnapshot_tilde', 'writesf', 'x_acoustics', 'x_arithmetic', 'x_array', 'x_file', 'x_qlist', 'x_scalar' ]