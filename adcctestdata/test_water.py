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
import tempfile
import unittest
import adcctestdata as atd

from pyscf import gto, scf


class TestWater(unittest.TestCase):
    def run_scf(self):
        fn = "water_321g.hdf5"
        if os.path.isfile(fn):
            return fn

        mol = gto.M(
            atom="""
            O 0 0 0
            H 0 0 1.795239827225189
            H 1.693194615993441 0 -0.599043184453037
            """,
            basis='sto-3g',
            unit="Bohr"
        )
        mf = scf.RHF(mol)
        mf.conv_tol = 1e-11
        mf.conv_tol_grad = 1e-10
        mf.kernel()
        return atd.dump_pyscf(mf, fn)

    def test_water_adc2(self):
        fn = self.run_scf()
        with tempfile.TemporaryDirectory() as tmpdir:
            atd.dump_reference(fn, "adc2", tmpdir + "/out.hdf5", n_states_full=2,
                               n_singlets=5, n_triplets=3, print_level=2)

    def test_water_cvs_adc2(self):
        fn = self.run_scf()
        with tempfile.TemporaryDirectory() as tmpdir:
            atd.dump_reference(fn, "cvs-adc2", tmpdir + "/out.hdf5", n_states_full=2,
                               n_singlets=3, n_triplets=3, print_level=2,
                               core_orbitals=[0, 7])

    def test_water_fc_adc2(self):
        fn = self.run_scf()
        with tempfile.TemporaryDirectory() as tmpdir:
            atd.dump_reference(fn, "adc2", tmpdir + "/out.hdf5", n_states_full=2,
                               n_singlets=3, n_triplets=3, print_level=2,
                               frozen_core=[0, 7])
