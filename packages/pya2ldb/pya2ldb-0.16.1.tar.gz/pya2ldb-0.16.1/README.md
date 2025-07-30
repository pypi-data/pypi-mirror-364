pyA2L
=====

[![Code Climate](https://codeclimate.com/github/christoph2/pyA2L/badges/gpa.svg)](https://codeclimate.com/github/christoph2/pyA2L)
[![Coverage Status](https://coveralls.io/repos/github/christoph2/pyA2L/badge.svg?branch=master)](https://coveralls.io/github/christoph2/pyA2L?branch=master)
[![Build Status](https://travis-ci.org/christoph2/pyA2L.svg)](https://travis-ci.org/christoph2/pyA2L)
[![Build status](https://ci.appveyor.com/api/projects/status/2sa0ascmg0b6lbt6?svg=true)](https://ci.appveyor.com/project/christoph2/pya2l)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GPL License](http://img.shields.io/badge/license-GPL-blue.svg)](http://opensource.org/licenses/GPL-2.0)

pyA2L is an [ASAM MCD-2MC](https://www.asam.net/standards/detail/mcd-2-mc/) processing library written in Python.

ASAM MCD-2MC, also known as ASAP2, is a non-XML file format for defining calibration parameters, measureable variables, and communication interface specific parameters, widely used in automotive applications.

ASAP2 is typically used together with CCP (CAN Calibration Protocol) or XCP (Universal Calibration Protocol). 

Supported Versions: [1.6](https://www.asam.net/standards/detail/mcd-2-mc/older/)

Installation
------------

- Via `pip`:
    ```shell
    $ pip install pya2ldb
    ```
    **IMPORTANT**: Package-name is `pya2ldb` **NOT** `pya2l`!!!

- From Github:
    - Clone / fork / download [pyA2Ldb repository](https://github.com/christoph2/pya2l).
    - Make sure you have a working Java installation on your system, like [AdoptOpenJDK](https://adoptopenjdk.net/) or [OpenJDK](https://openjdk.java.net/).
    - Download and install `ANTLR 4.11.1`:
        - `curl -O -C - -L https://www.antlr.org/download/antlr-4.11.1-complete.jar`
        - Add `ANTLR` to your `CLASSPATH` environment variable, e.g.: `export CLASSPATH=$CLASSPATH:~/jars/antlr-4.11.1-complete.jar` (you may put this in your `.bashrc`, `.zshrc`, ...).
    - Run setup-script: `python setup.py develop`

Getting Started
---------------
here is a basic example:
```python
from pya2l import DB
import pya2l.model as model

db = DB()
base_dir = "examples/"
a2l_file = "ASAP2_Demo_V161"
try:
    session = db.import_a2l(f"{base_dir}{a2l_file}.a2l")
except OSError:
    print("a2ldb for this file already exists, using it instead")
    session = db.open_existing(f"{base_dir}{a2l_file}.a2ldb")

measurements = session.query(model.Measurement).order_by(model.Measurement.name).all()
for m in measurements:
    print(f"{m.name:48} {m.datatype:12} 0x{m.ecu_address.address:08x}")
```


----------

**pyA2L is part of pySART (Simplified AUTOSAR-Toolkit for Python).**
----------
