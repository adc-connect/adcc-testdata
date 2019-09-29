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
from .MpTasks import TaskMp1, TaskMp2Td2, TaskMp3
from .PiTasks import TaskPia, TaskPib

from pyadcman import CtxMap

# Documentation for the parameters:
#   adcman/adcman/qchem/params_reader.h
#   adcman/adcman/qchem/params_reader.C


class AdcTaskBase:
    # TODO copy function docstrings from c++

    @classmethod
    def adc_level(cls):
        if cls.name == "adc0":
            return 0
        if cls.name == "adc1":
            return 1
        if cls.name in ["adc2", "adc2x"]:
            return 2
        if cls.name == "adc3":
            return 3
        else:
            raise ValueError("Level cannot be determined for method " + cls.name)

    @classmethod
    def parameters(cls, **kwargs):
        adc_variant = kwargs.get("adc_variant", [])

        # Determine the variant string
        variant = cls.name
        if variant == "adc2":
            variant = "adc2s"
        if "ri" in adc_variant:
            variant = "ri_" + variant
        if "sos" in adc_variant:
            variant = "sos_" + variant
        if "cvs" in adc_variant:
            variant = "cvs_" + variant

        params = CtxMap({"adc_pp": "1"})
        params["adc_pp/" + variant] = "1"
        cls.add_common_adc_params_to(params.submap("adc_pp/" + variant), **kwargs)
        return params

    @classmethod
    def insert_print_subtree(cls, tree, print_level=1, adc_variant=[], **kwargs):
        tree["print/print_level"] = str(print_level)

        nampl = 0
        if print_level >= 1:
            nampl = 2
        elif print_level >= 2:
            nampl = 20
        elif print_level >= 3:
            nampl = 40
        else:
            nampl = 60
        tree["print/nampl"] = str(nampl)

        # No PCM at the moment
        tree["print/pcm"] = "0"  # False
        tree["print/cvs"] = "0"
        tree["print/sf"] = "0"
        if "cvs" in adc_variant:
            tree["print/cvs"] = "1"
        if "sf" in adc_variant:
            tree["print/sf"] = "1"

        return tree

    @classmethod
    def add_common_adc_params_to(cls, tadc, restricted=False, n_singlets=0, n_triplets=0,
                                 n_states=0, **kwargs):
        adc_variant = kwargs.get("adc_variant", [])
        cls.insert_print_subtree(tadc, **kwargs)

        # Insert intermediates for appropriate ADC level
        tadc["prereq/adc{}_im".format(cls.adc_level())] = "1"

        # Build restricted / unrestricted subtree
        if restricted:
            if "sf" in adc_variant:
                raise ValueError("Cannot run spin-flip for restricted references.")
            if n_states > 0:
                raise ValueError("Cannot use n_states for restricted references.")
            if n_singlets + n_triplets == 0:
                raise ValueError("n_singlets + n_triplets needs to be larger 0 for "
                                 "restricted references.")

            tadc["rhf"] = "1"
            tadc["uhf"] = "0"
            if n_singlets > 0:
                tadc["rhf/singlets"] = "1"
                cls.add_spin_params_to(tadc.submap("rhf/singlets"), "singlet", n_singlets, **kwargs)
            else:
                tadc["rhf/singlets"] = "0"

            if n_triplets > 0:
                tadc["rhf/triplets"] = "1"
                cls.add_spin_params_to(tadc.submap("rhf/triplets"), "triplet", n_triplets, **kwargs)
            else:
                tadc["rhf/triplets"] = "0"
        else:
            if n_singlets > 0 or n_triplets > 0:
                raise ValueError("Cannot use n_singlets or n_triplets for unrestricted references.")
            if n_states == 0:
                raise ValueError("n_states needs to be larger 0 for unrestricted references.")

            tadc["rhf"] = "0"
            tadc["uhf"] = "1"
            cls.add_spin_params_to(tadc.submap("uhf"), "any", n_states, **kwargs)

    @classmethod
    def add_spin_params_to(cls, tspin, spin, n_states, **kwargs):
        """
        Add the singlet/triplet/any parameters to `tspin`, where `spin`
        is "singlet", "triplet" or "any" and `n_states` is the number of states
        to be computed.
        """
        # TODO This assumes only a single irrep
        irrep = "0"
        tspin[irrep] = "1"  # enable irrep
        cls.add_irrep_params_to(tspin.submap(irrep), spin, irrep, n_states, **kwargs)

    @classmethod
    def add_irrep_params_to(cls, tirrep, spin, irrep, n_states, adc_variant=[], **kwargs):
        """
        Add the subtree data for a particular irrep. Adds keys like:
          - solver
          - spin
          - ...

        `tirrep` is the subtree for this irrep, `spin` is "singlet", "triplet" or "any",
        `n_states` is the number of states of this irrep to be computed
        """

        # Setup spin-related things
        tirrep["spin"] = spin
        tirrep["irrep"] = irrep
        tirrep["nroots"] = str(n_states)

        # Force using the ADC(3) method, which requires precomputation of pib intermediates
        tirrep["direct"] = "0"

        # Compute density matrices
        tirrep["optdm"] = "1"
        tirrep["opdm"] = "1"

        # Set spin-flip if needed
        tirrep["spin_flip"] = "0"
        if "sf" in adc_variant:
            tirrep["spin_flip"] = "1"

        # Two-photon absorption
        # tirrep["tpa"] = "1"

        # Properties
        for pt in ["prop", "tprop"]:
            tirrep[pt + "/."] = "1"
            tirrep[pt + "/dipole"] = "1"
            tirrep[pt + "/rsq"] = "0"

        # Setup solver-related parameters inside the subtree
        cls.add_solver_params_to(tirrep, n_states, **kwargs)

    @classmethod
    def add_solver_params_to(cls, tirrep, n_states, n_guess_singles=None, n_guess_doubles=None,
                             solver=None, conv_tol=None, residual_min_norm=None, max_iter=None,
                             max_subspace=None, **kwargs):
        """
        Add parameters which distinguish between the various adc methods to the parameter tree.
        `n_states` is the number of states to compute in this very irrep.
        Includes keys like:
          - solver
          - davidson
          - nguess_singles
          - nguess_doubles
          - ...
        """
        # Set number of guesses
        tirrep["nguess_singles"] = str(n_guess_singles)
        tirrep["nguess_doubles"] = str(n_guess_doubles)
        if n_guess_singles + n_guess_doubles < n_states:
            tirrep["nguess_singles"] = str(n_states - n_guess_doubles)

        # Set solver parameters
        tirrep["solver"] = solver
        tirrep[solver + "/convergence"] = str(conv_tol)
        tirrep[solver + "/maxiter"] = str(max_iter)
        tirrep[solver + "/threshold"] = str(residual_min_norm)

        # Special adjustment for davidson
        if solver == "davidson":
            if max_subspace == 0:
                max_subspace = 5 * n_states
            elif max_subspace < n_states:
                max_subspace = 2 * n_states
            tirrep["davidson/maxsubspace"] = str(max_subspace)


class TaskAdc0(AdcTaskBase):
    dependencies = []
    name = "adc0"


class TaskAdc1(AdcTaskBase):
    dependencies = [TaskMp1]
    name = "adc1"


class TaskAdc2(AdcTaskBase):
    dependencies = [TaskMp2Td2]
    name = "adc2"


class TaskAdc2x(AdcTaskBase):
    dependencies = [TaskMp2Td2]
    name = "adc2x"


class TaskAdc3(AdcTaskBase):
    dependencies = [TaskMp3, TaskPia, TaskPib]
    name = "adc3"
