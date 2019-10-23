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
import os
import adcctestdata as atd

from pyscf import gto, scf

if not os.path.isfile("hf3.hdf5"):
    mol = gto.M(
        atom='H 0 0 0;'
             'F 0 0 2.5',
        basis='6-31G',
        unit="Bohr",
        spin=2  # =2S, ergo triplet
    )
    mf = scf.UHF(mol)
    mf.conv_tol = 1e-14
    mf.grad_conv_tol = 1e-10
    mf.kernel()
    atd.dump_pyscf(mf, "hf3.hdf5")

atd.dump_reference("hf3.hdf5", "adc2", "hf3_sf_adc2.hdf5", n_states_full=2,
                   n_spin_flip=5, print_level=100)
