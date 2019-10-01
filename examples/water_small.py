#!/usr/bin/env python3
## vi: tabstop=4 shiftwidth=4 softtabstop=4 expandtab
## ---------------------------------------------------------------------
##
## Copyright (C) 2019 by Michael F. Herbst
##
## This file is part of adcc-testdata.
##
## adcc-testdata is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published
## by the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## adcc-testdata is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with adcc-testdata. If not, see <http://www.gnu.org/licenses/>.
##
## ---------------------------------------------------------------------
import os

from pyscf import gto, scf

import adcctestdata as atd

if not os.path.isfile("water_small.hdf5"):
    mol = gto.M(
        atom="""
        O 0 0 0
        H 0 0 1.795239827225189
        H 1.693194615993441 0 -0.599043184453037
        """,
        basis='3-21g',
        unit="Bohr"
    )
    mf = scf.RHF(mol)
    mf.conv_tol = 1e-13
    mf.conv_tol_grad = 1e-12
    mf.diis = scf.EDIIS()
    mf.diis_space = 3
    mf.max_cycle = 500
    mf.kernel()

    atd.dump_pyscf(mf, "water_small.hdf5")

atd.dump_reference("water_small.hdf5", "adc2", "water_small_adc2.hdf5", n_states_full=2,
                   n_singlets=5, n_triplets=3, print_level=100)
