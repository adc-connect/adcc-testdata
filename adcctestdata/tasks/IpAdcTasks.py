#!/usr/bin/env python3
## vi: tabstop=4 shiftwidth=4 softtabstop=4 expandtab
## ---------------------------------------------------------------------
##
## Copyright (C) 2020 by Michael F. Herbst
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
from .MpTasks import TaskHf, TaskMp2
from .OtherTasks import TaskDysonExpansionMethod

from pyadcman import CtxMap

# Documentation for the parameters:
#   adcman/adcman/qchem/params_reader.h
#   adcman/adcman/qchem/params_reader.C


class IpAdcTaskBase:
    @classmethod
    def adc_level(cls):
        if cls.name == "ipadc0":
            return 0
        if cls.name == "ipadc2":
            return 2
        if cls.name == "ipadc3":
            return 3
        else:
            raise ValueError("Level cannot be determined for method " + cls.name)

    @classmethod
    def parameters(cls, **kwargs):
        adc_variant = kwargs.get("adc_variant", [])
        if adc_variant:
            raise ValueError("Right now IP-ADC has no variants implemented.")

        # Determine the variant string
        assert cls.name[0:2] == "ip"
        variant = cls.name[2:]
        # TODO Stuff in PP adc tree
        # if "ri" in adc_variant:
        #     variant = "ri_" + variant
        # if "sos" in adc_variant:
        #     variant = "sos_" + variant
        # if "cvs" in adc_variant:
        #     variant = "cvs_" + variant

        params = CtxMap({"adc_ip": "1"})
        params["adc_ip/" + variant] = "1"
        cls.add_common_adc_params_to(params.submap("adc_ip/" + variant), **kwargs)
        return params

    @classmethod
    def insert_print_subtree(cls, tree, print_level=1, adc_variant=[], **kwargs):
        # TODO complete code duplication with PP stuff
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
    def add_common_adc_params_to(cls, tadc, restricted=False, n_ipalpha=0,
                                 n_ipbeta=0, ground_state_density=None,
                                 **kwargs):
        cls.insert_print_subtree(tadc, **kwargs)

        # Purge n_states parameter if it's still in the kwargs
        kwargs.pop("n_states", None)

        # Insert intermediates for appropriate ADC level
        tadc["prereq/adc{}_im".format(cls.adc_level())] = "1"

        # Insert effective transition moments
        if cls.adc_level() <= 2:
            if ground_state_density is not None:
                raise ValueError(f"Explicit selection of ground state density "
                                 "order not compatible with "
                                 f"IP-ADC{cls.adc_level()}")
            tadc["prereq/adc{}_etm".format(cls.adc_level())] = "1"
        elif ground_state_density is None or ground_state_density == "mp2":
            tadc["prereq/adc3_etm"] = "2"
        elif ground_state_density == "mp3":
            tadc["prereq/adc3_etm"] = "3"
        elif ground_state_density == "dyson":
            tadc["prereq/adc3_etm"] = "3+"
        else:
            raise ValueError(f"ground_state_density == {ground_state_density} "
                             "not implemented for IP-ADC(3)")

        # Build restricted / unrestricted subtree
        if restricted:
            if n_ipalpha > 0:
                raise ValueError("Adcman only computes beta ionisations "
                                 "for restricted references.")

            tadc["rhf"] = "1"
            tadc["uhf"] = "0"
            cls.add_state_params_to(tadc.submap("rhf"), "restr_beta",
                                    n_ipbeta, **kwargs)
            cls.add_state2state_params_to(tadc.submap("rhf"), "restr_beta",
                                          n_ipbeta, n_ipbeta, **kwargs)
        else:
            tadc["rhf"] = "0"
            tadc["uhf"] = "1"
            if n_ipalpha > 0:
                tadc["uhf/alphas"] = "1"
                cls.add_state_params_to(tadc.submap("uhf/alphas"),
                                        "unrestr_alpha", n_ipalpha, **kwargs)
                cls.add_state2state_params_to(tadc.submap("uhf/alphas"),
                                              "unrestr_alpha", n_ipalpha,
                                              n_ipalpha, **kwargs)
            if n_ipbeta > 0:
                tadc["uhf/betas"] = "1"
                cls.add_state_params_to(tadc.submap("uhf/betas"), "unrestr_beta",
                                        n_ipbeta, **kwargs)
                cls.add_state2state_params_to(tadc.submap("uhf/betas"),
                                              "unrestr_beta", n_ipbeta,
                                              n_ipbeta, **kwargs)

    @classmethod
    def add_state_params_to(cls, tspin, spin, n_states, **kwargs):
        """
        Add the unrestr_alpha/unrestr_beta/restr_beta parameters to `tspin`, where
        `spin` is "unrestr_alpha", "unrestr_beta" or "restr_beta" and n_states is
        the number of states to be computed.
        """
        # TODO identical to PP case
        # TODO This assumes only a single irrep
        irrep = "0"
        tspin[irrep] = "1"  # enable irrep
        cls.add_state_irrep_params_to(tspin.submap(irrep), spin, irrep,
                                      n_states, **kwargs)

    @classmethod
    def add_state_irrep_params_to(cls, tirrep, spin, irrep, n_states,
                                  adc_variant=[], **kwargs):
        """
        Add the subtree data for a particular irrep. Adds keys like:
          - solver
          - spin
          - ...

        `tirrep` is the subtree for this irrep, `spin` is "singlet", "triplet"
        or "any",`n_states` is the number of states of this irrep to be computed
        """
        # TODO almost identical to PP case

        # Setup spin-related things
        tirrep["spin"] = spin
        tirrep["irrep"] = irrep
        tirrep["nroots"] = str(n_states)

        # TODO This exists extra in PP
        # # Force using the ADC(3) method, which requires precomputation
        # # of pib intermediates
        # tirrep["direct"] = "0"

        # Compute density matrices
        # tirrep["optdm"] = "1"
        tirrep["opdm"] = "1"

        # TODO This exists extra in PP
        # # Set spin-flip if needed
        # tirrep["spin_flip"] = "0"
        # if "sf" in adc_variant:
        #     tirrep["spin_flip"] = "1"

        # Properties
        for pt in ["prop"]:  # , "tprop"]:
            tirrep[pt + "/."] = "1"
            tirrep[pt + "/dipole"] = "1"
            tirrep[pt + "/rsq"] = "0"

        # Setup solver-related parameters inside the subtree
        cls.add_solver_params_to(tirrep, n_states, **kwargs)

    @classmethod
    def add_solver_params_to(cls, tirrep, n_states, n_guess_h=0,
                             n_guess_p2h=0, solver="davidson", conv_tol=1e-6,
                             residual_min_norm=1e-12, max_iter=0,
                             max_subspace=60, **kwargs):
        """
        Add parameters which distinguish between the various adc methods to the
        parameter tree. `n_states` is the number of states to compute in this
        very irrep. Includes keys like:
          - solver
          - davidson
          - nguess_h
          - nguess_p2h
          - ...
        """
        # Set number of guesses
        tirrep["nguess_h"] = str(n_guess_h)
        tirrep["nguess_p2h"] = str(n_guess_p2h)
        if n_guess_h + n_guess_p2h < n_states:
            tirrep["nguess_h"] = str(n_states - n_guess_p2h)

        # TODO This part until the end of the function is identical to PP
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

    @classmethod
    def add_state2state_params_to(cls, tspin, spin, n_states1, n_states2,
                                  **kwargs):
        """
        Parameters for state2state properties
        """
        # TODO This is identical to PP
        tspin["isr"] = "1"
        irrep1 = irrep2 = "0"  # TODO Assume only one irrep

        tirrep = tspin.submap("isr/" + irrep1 + "-" + irrep2)
        tirrep["."] = "1"      # Enable state2state for irrep
        tirrep["optdm"] = "1"  # Transition density matrices
        tirrep["tprop"] = "1"  # Transition properties

        if spin in ["s2t", "any"]:
            # Spin-orbit coupling
            tirrep["tprop/soc"] = "0"
        if spin != "s2t":
            tirrep["tprop/dipole"] = "1"
            tirrep["tprop/rsq"] = "0"


class TaskIpAdc0(IpAdcTaskBase):
    dependencies = [TaskHf]
    name = "ipadc0"


class TaskIpAdc2(IpAdcTaskBase):
    dependencies = [TaskMp2]
    name = "ipadc2"


class TaskIpAdc3(IpAdcTaskBase):
    dependencies = [TaskDysonExpansionMethod]
    name = "ipadc3"
