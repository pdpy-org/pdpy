#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# **************************************************************************** #
# This file is part of the pdpy project
# Copyright (C) 2021 Fede Camara Halac
# **************************************************************************** #
""" Translator example """

from pdpy import Translator

# initialize the translator object with an input file
trans = Translator('./tests/hello-world.pd')

# run the translator
trans()

# translate to json
trans.translate('json')

# print the json string to console
# print(trans.json)

# write the translation to JSON format to disk
trans.write_json()

# translate to xml
# write the translation to XML format to disk
trans.translate('xml').write_xml()

# write a pd file using the json translation as input
trans.write_pd_ref()
