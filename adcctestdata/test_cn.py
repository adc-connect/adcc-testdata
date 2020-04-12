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
import adcctestdata as atd
import numpy.testing

from pyscf import gto, scf


def assert_allclose(x, y):
    numpy.testing.assert_allclose(x, y, atol=1e-6)


class TestCn(unittest.TestCase):
    def run_scf(self):
        fn = "cn_sto3g.hdf5"
        if os.path.isfile(fn):
            return fn

        mol = gto.M(
            atom="""
            C 0 0 0
            N 0 0 2.2143810738114829
            """,
            spin=1,
            basis='sto-3g',
            unit="Bohr",
        )
        mf = scf.UHF(mol)
        mf.conv_tol = 1e-11
        mf.conv_tol_grad = 1e-10
        mf.diis = scf.EDIIS()
        mf.diis_space = 5
        mf.max_cycle = 500
        mf.kernel()
        return atd.dump_pyscf(mf, fn)

    def test_cn_adc2(self):
        fn = self.run_scf()
        with tempfile.TemporaryDirectory() as tmpdir:
            res = atd.dump_reference(fn, "adc2", tmpdir + "/out.hdf5",
                                     n_states_full=2, n_states=6, print_level=2)
            assert_allclose(res["adc/state/eigenvalues"][()],
                            np.array([0.14185414, 0.14185414, 0.1739203,
                                      0.28945843, 0.299935, 0.299935]))

    def test_cn_cvs_adc2(self):
        fn = self.run_scf()
        with tempfile.TemporaryDirectory() as tmpdir:
            res = atd.dump_reference(fn, "cvs-adc2", tmpdir + "/out.hdf5",
                                     n_states_full=2, n_states=5, print_level=2,
                                     core_orbitals=[0, 10])
            assert_allclose(res["adc/state/eigenvalues"][()],
                            np.array([14.74651745, 14.84335613, 14.84335613,
                                      15.01768321, 15.01768321]))

    def test_cn_fc_adc2(self):
        fn = self.run_scf()
        with tempfile.TemporaryDirectory() as tmpdir:
            res = atd.dump_reference(fn, "adc2", tmpdir + "/out.hdf5",
                                     n_states_full=2, n_states=5, print_level=2,
                                     frozen_core=[0, 10])
            assert_allclose(res["adc/state/eigenvalues"][()],
                            np.array([0.1419152, 0.1419152, 0.17400268,
                                      0.28946901, 0.29998021]))

    def test_cn_ipadc3(self):
        fn = self.run_scf()
        # TODO Dump reference not yet implemented for IP-ADC
        res = atd.run_adcman(fn, "ipadc3", n_ipbeta=5, n_ipalpha=5, print_level=2,
                             ground_state_density="dyson")
        αs = np.array([res[f"/adc_ip/adc3/uhf/alphas/0/ip{i}/energy"]
                       for i in range(5)])
        βs = np.array([res[f"/adc_ip/adc3/uhf/betas/0/ip{i}/energy"]
                       for i in range(5)])
        assert_allclose(αs, np.array([0.4453358, 0.4453358, 0.4520745,
                                      0.5394661, 0.5394661]))
        assert_allclose(βs, np.array([0.4162376, 0.4162376, 0.4480881,
                                      0.6610674, 0.6610675]))
