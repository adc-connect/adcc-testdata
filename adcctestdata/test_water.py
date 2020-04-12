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
import tempfile
import unittest
import numpy as np

from pyscf import gto, scf
from numpy.testing import assert_allclose

import adcctestdata as atd


class TestWater(unittest.TestCase):
    def run_scf(self):
        fn = "water_sto3g.hdf5"
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
            res = atd.dump_reference(fn, "adc2", tmpdir + "/out.hdf5",
                                     n_states_full=2, n_singlets=5,
                                     n_triplets=3, print_level=2)
            assert_allclose(res["adc/singlet/eigenvalues"][()],
                            np.array([0.47051314, 0.57255495, 0.59367335,
                                      0.71296882, 0.83969732]))
            assert_allclose(res["adc/triplet/eigenvalues"][()],
                            np.array([0.40288477, 0.4913253, 0.52854722]))

    def test_water_cvs_adc2(self):
        fn = self.run_scf()
        with tempfile.TemporaryDirectory() as tmpdir:
            res = atd.dump_reference(fn, "cvs-adc2", tmpdir + "/out.hdf5",
                                     n_states_full=2, n_singlets=3, n_triplets=3,
                                     print_level=2, core_orbitals=[0, 7])
            assert_allclose(res["adc/singlet/eigenvalues"][()],
                            np.array([20.0045422, 20.08771799, 21.82672127]))
            assert_allclose(res["adc/triplet/eigenvalues"][()],
                            np.array([19.95732865, 20.05239094, 21.82672127]))

    def test_water_fc_adc2(self):
        fn = self.run_scf()
        with tempfile.TemporaryDirectory() as tmpdir:
            res = atd.dump_reference(fn, "adc2", tmpdir + "/out.hdf5",
                                     n_states_full=2, n_singlets=3, n_triplets=3,
                                     print_level=2, frozen_core=[0, 7])
            assert_allclose(res["adc/singlet/eigenvalues"][()],
                            np.array([0.47048699, 0.57249152, 0.59374785]))
            assert_allclose(res["adc/triplet/eigenvalues"][()],
                            np.array([0.40290068, 0.4913562, 0.52852212]))

    def test_water_ipadc3(self):
        fn = self.run_scf()
        # TODO Dump reference not yet implemented for IP-ADC
        res = atd.run_adcman(fn, "ipadc3", n_ipbeta=5, print_level=2,
                             ground_state_density="dyson")
        ips = np.array([res[f"/adc_ip/adc3/rhf/0/ip{i}/energy"]
                        for i in range(5)])
        assert_allclose(ips, np.array([0.315887216, 0.391410529, 0.619760418,
                                       1.067238764, 1.070609008]))
