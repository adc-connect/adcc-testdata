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

if not os.path.isfile("cn.hdf5"):
    mol = gto.M(
        atom="""
        C 0 0 0
        N 0 0 2.2143810738114829
        """,
        basis='cc-pvdz',
        unit="Bohr",
        spin=1,
        verbose=4,
    )
    mf = scf.UHF(mol)
    mf.conv_tol = 1e-11
    mf.conv_tol_grad = 1e-10
    mf.diis = scf.EDIIS()
    mf.diis_space = 3
    mf.max_cycle = 500
    mf.kernel()

    atd.dump_pyscf(mf, "cn.hdf5")

atd.dump_reference("cn.hdf5", "adc2", "cn_adc2.hdf5", n_states_full=3,
                   n_states=5, print_level=100)
