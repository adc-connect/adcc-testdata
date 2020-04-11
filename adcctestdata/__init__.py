#!/usr/bin/env python3
## vi: tabstop=4 shiftwidth=4 softtabstop=4 expandtab
## ---------------------------------------------------------------------
##
## Copyright (C) 2019 by Michael F. Herbst
##
## This file is part of adcc-testdata.
##
## adcc-testdata is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published
## by the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## adcc-testdata is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with adcc-testdata. If not, see <http://www.gnu.org/licenses/>.
##
## ---------------------------------------------------------------------

try:
    import pyadcman  # noqa: F401
except ImportError:
    raise ImportError("Package pyadcman not found. Please install this "
                      "package first.")

from .dump_pyscf import dump_pyscf
from .run_adcman import run_adcman
from .HdfProvider import HdfProvider
from .dump_reference import dump_reference

__all__ = ["HdfProvider", "run_adcman", "dump_pyscf", "dump_reference"]

__version__ = "0.1.0"
__license__ = "GPL v3"
__authors__ = ["Michael F. Herbst"]
__email__ = "developers@adc-connect.org"
